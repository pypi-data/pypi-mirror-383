from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator

import pandas as pd
import xgboost as xgb
import numpy as np
import random
from astropy.table import Table
import pandas as pd
import importlib.resources as resources
import pathlib
import requests
from astropy.table import Table

import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import seaborn as sns
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 12
plt.rcParams['font.family'] = 'serif'

# Cache directory for large CSVs
CACHE_DIR = pathlib.Path.home() / ".seshat_classifier" / "data"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# URLs for hosted large CSVs
CSV_URLS = {
    "training_set.csv": "https://bcrompvoets.github.io/assets/files/seshat/training_set.csv",
    "training_set_cosmological.csv": "https://bcrompvoets.github.io/assets/files/seshat/training_set_cosmological.csv",
    "training_set_AGB.csv": "https://bcrompvoets.github.io/assets/files/seshat/training_set_AGB.csv",
}


# Load a small CSV packaged with the code
def _load_small_csv(name):
    with resources.files("seshat_classifier").joinpath("data",name).open("rb") as f:
        return pd.read_csv(f)
def _load_big_csv(name):
    url = CSV_URLS[name]
    path = CACHE_DIR / name
    etag_path = CACHE_DIR / f"{name}.etag"

    # Try to use cache if it exists
    if path.exists():
        try:
            head = requests.head(url, timeout=5)
            if head.status_code == 200:
                remote_etag = head.headers.get("ETag")
                local_etag = etag_path.read_text().strip() if etag_path.exists() else None
                if remote_etag and remote_etag == local_etag:
                    return pd.read_csv(path)
        except requests.RequestException:
            print(f"[seshat_classifier] Offline — using cached {name}")
            return pd.read_csv(path)

    # If we get here, we either have no file or need to update it
    try:
        print(f"[seshat_classifier] Downloading {name}...")
        r = requests.get(url, stream=True, timeout=10)
        r.raise_for_status()
        path.write_bytes(r.content)

        # Save ETag
        etag = r.headers.get("ETag")
        if etag:
            etag_path.write_text(etag)

        print(f"[seshat_classifier] Saved to {path}")
        return pd.read_csv(path)

    except requests.RequestException as e:
        if path.exists():
            print(f"[seshat_classifier] Warning: Could not update {name} ({e}), using cached file")
            return pd.read_csv(path)
        else:
            raise FileNotFoundError(
                f"Could not download {name} and no cached copy exists. "
                "Please connect to the internet and try again."
            )

def relabel_training_classes(keep_class,inp_df,real=None):
    """ This function relabels the classes in terms of numbers, assigned at runtime.
    
    Inputs:
    keep_class (list): The classes to be kept, can be "YSO", 
    inp_df (DataFrame): The input dataframe with the original classes.
    real (DataFrame): The real dataframe to be classified, if available.
    
    Returns:
    inp_new (DataFrame): The input dataframe with the relabeled classes.
    real (DataFrame): The real dataframe with the relabeled classes, if available.
    keep_class_new (list): The new list of classes, in the order they were relabeled.
    """
    possible_classes = ["YSO", "FS", "WD", "BD", "Gal"]

    # Make new dataframe with just the classes requested
    inp_new = inp_df[inp_df["Class"].isin(keep_class)].copy()

    # If contaminant class is requested, make new class of everything not otherwise requested
    if "Contaminant" in keep_class:
        inp_new.loc[~inp_new["Class"].isin(keep_class), "Class"] = "Contaminant"

    # Make an ordered list of what the requested classes are
    keep_class_new = [p for p in possible_classes if p in keep_class]
    if 'Contaminant' in keep_class:
        keep_class_new.append('Contaminant')

    # Write a new label that gives an integer value for each class.
    inp_new["Class_Label"] = pd.Categorical(inp_new["Class"], categories=keep_class_new).codes
    
    # Relabel the real set as well.
    if real is not None:
        real["Class_Label"] = pd.Categorical(real["Class"], categories=keep_class_new).codes
        return inp_new, real, keep_class_new

    return inp_new, keep_class_new

def classify(real, 
            cosmological=False,
            classes=["YSO", "FS", "BD", "WD", "Gal"],
            return_test=True,
            threads=1):
    """ This function is the main function of SESHAT. It takes a real dataset and classifies it into the provided classes, with probabilities.
    
    Inputs:
    real (DataFrame or Table): The input catalog, either a FITS table or a apandas DataFrame, with columns as described in the README.
    cosmological (bool): Whether the catalog is of a cosmological field
    classes (list): The classes to be assigned, can be "YSO", "FS", "BD", "WD", "Gal, or "Contaminant" (the latter is still under development, use at own risk)
    return_test (bool): Whether to return the test set original and predicted classifications, and predicted probabilities
    threads (int): The number of threads to use when classifying.

    Returns:
    real (DataFrame or Table): A copy of the input catalog, now with classifications and probabilities
    (optional) test (DataFrame): A pandas DataFrame containing the following columns: the true class, the predicted class, and a column each for each class specified in the input classes list.
    """
    # Load small packaged CSV
    veg_jy = {f: v for (f, v) in _load_small_csv("veg_zps_spitzer_2mass_jwst.csv").values}

    # Convert Table to pandas if needed
    if isinstance(real, Table):
        real = real.to_pandas()
        table = True
    else:
        table = False

    # Load appropriate large input data CSV
    if cosmological:
        inp_df = _load_big_csv("training_set_cosmological.csv")
    else:
        inp_df = _load_big_csv("training_set.csv")

    if "AGB" in classes:
        inp_df = _load_big_csv("training_set_AGB.csv")     


    # Determine filters to use
    filters = [f for f in real.columns if f in veg_jy.keys()]
    
    #Relabel/select classes
    inp_df, new_classes = relabel_training_classes(classes,inp_df)
    
    # Prepare data
    dtrain, dval, dte, dreal = prep_all_dat(inp_df, real, filters)
    fcd_columns = [col for col in dtrain.columns if ('-' in col)]
    
    # Train XGBoost model
    xgb_cls = xgb.XGBClassifier(
        n_jobs=threads,
        gamma=15,
        subsample=0.3,
        max_depth=1,
        learning_rate=0.01,        
        objective="multi:softprob",
        num_class=dtrain['Class_Label'].nunique(),
        n_estimators=100000,        
        eval_metric='mlogloss',
        early_stopping_rounds=500,
        tree_method="hist"
    )

    # fit with validation and early stopping
    xgb_cls.fit(
        dtrain[fcd_columns],
        dtrain['Class_Label'],
        eval_set=[(dval[fcd_columns], dval['Class_Label'])],
        verbose=False
    )

    # Calibrate probabilities
    try:
        calibrator = CalibratedClassifierCV(FrozenEstimator(xgb_cls), method="sigmoid")
        calibrator.fit(dval[fcd_columns],dval['Class_Label'])
    except:
        calibrator = None
        print("Calibrator failed")


    # Get predictions for real set
    if calibrator is not None:
        probs = calibrator.predict_proba(dreal[fcd_columns])
    else:
        probs = xgb_cls.predict_proba(dreal[fcd_columns])
    real = get_preds(probs=probs, df=real, display_labels=new_classes)
    if table:
        real = Table.from_pandas(real)
    
    # Get predictions for test set
    if return_test:
        classes= np.array(new_classes)[np.array(dte['Class_Label'].astype(int))]
        test_df = pd.DataFrame({"Class":classes})
        if calibrator is not None:
            probs = calibrator.predict_proba(dte[fcd_columns])
        else:
            probs = xgb_cls.predict_proba(dte[fcd_columns])
        test_df = get_preds(probs=xgb_cls.predict_proba(dte[fcd_columns]), df=test_df, display_labels=new_classes)
        return (real, test_df, new_classes)
    
    return real


def get_preds(probs, df,display_labels):
    """ Get a column for each label with the probability for each object. Also get a column with the assigned label based on the greatest probability."""
    classes = np.array(display_labels)[np.array(probs.argmax(axis=1))]
    df = df.assign(Predicted_Class=classes).join(pd.DataFrame(probs, columns=[f"Prob {l}" for l in display_labels], index=df.index))
    return df


def cm_custom(y_true, y_pred, display_labels=None, ax=None, cmap='Greys'):
    """ Create a confusion matrix with custom annotations showing both normalized values and counts.
    Inputs:
    y_true (array-like): True labels.
    y_pred (array-like): Predicted labels.
    display_labels (list): List of labels to display on axes.
    ax (matplotlib axis): Axis to plot on. If None, a new figure and axis are created.
    cmap (str): Colormap to use for the heatmap.
    
    Returns:
    ax (matplotlib axis): The axis with the confusion matrix plot."""
    # Get confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=display_labels)
    cm_norm = cm.astype('float') / cm.sum(axis=1, keepdims=True)

    # Create custom annotations: normalized (first line), counts (second line)
    annot = np.empty_like(cm).astype(str)
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            norm_val = f"{cm_norm[i, j]:.2f}"
            count_val = f"{cm[i, j]}"
            annot[i, j] = f"{norm_val}\n{count_val}"

    # If no axis is given, create one
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 6))
    
    # Protect the display_labels list from being over-written
    display_labels = display_labels.copy()
    
    # Edit labels based on length of classes
    if (len(display_labels) <= 3):
        if 'FS' in display_labels:
            display_labels[display_labels.index('FS')] = 'Field Star'
        if 'BD' in display_labels:  
            display_labels[display_labels.index('BD')] = 'Brown Dwarf'
        if 'WD' in display_labels:
            display_labels[display_labels.index('WD')] = 'White Dwarf'
        if 'Gal' in display_labels:
            display_labels[display_labels.index('Gal')] = 'Galaxy'
    if len(display_labels) > 3:
        if 'Contaminant' in display_labels:
            display_labels[display_labels.index('Contaminant')] = 'Cont.'
    # Draw heatmap with custom annotations
    sns.heatmap(
        cm_norm,
        annot=annot,
        fmt='',
        cmap=cmap,
        vmin=0,
        vmax=1,
        square=True,
        xticklabels=display_labels,
        yticklabels=display_labels,
        ax=ax,
        cbar_kws={'label': 'Normalized value'}
    )

    ax.set_xlabel('Predicted label')
    ax.set_ylabel('True label')

    return ax


def add_noise(filters, df,df_real):
    """ Add noise based on the wavelength as determined from real data. 
    
    Inputs:
    filters (list): The filters to be used.
    df (DataFrame): The dataframe to which noise will be added.
    df_real (DataFrame): The real dataframe from which errors will be drawn.
    
    Returns:
    df_new (DataFrame): The dataframe with noise added."""

    # Make sure no infinite datapoints
    df = df.replace([np.inf, -np.inf], np.nan)
    
    # Randomly add or subtract error (i.e. +/- noise)
    errs = np.array([np.random.choice(df_real.dropna(subset=[f,'e_'+f])[['e_'+f]].values.ravel(),len(df)) for f in filters]).T
    noise = np.random.normal(loc=0, scale=errs, size=(len(df), len(filters)))

    df_tmp = df.copy()
    df_tmp[filters] = df[filters].to_numpy() + noise
    df_new = pd.concat([df, df_tmp], ignore_index=True)

    return df_new
        


def add_null_faint(df, filters, limiting_mags=None, frac = 0.1):
    """ Add null values for some fraction of the data, where the null values are placed where the filter
    is fainter than the limiting magnitude of the observation. The limiting magnitude is determined
    by shifting the entire SED such that the brightest filter is 2-4 mags brighter than the limiting mag.
    Inputs:
    df (DataFrame): The dataframe to which nulls will be added.
    filters (list): The filters to be used.
    limiting_mags (dict): The limiting magnitudes for each filter.
    frac (float): The fraction of the data to which nulls will be added.
    
    Returns:
    df (DataFrame): The dataframe with nulls added."""

    if limiting_mags is None:
        raise ValueError("Must input limiting mags of observation!")

    # Define new sample for nans
    df_nonan = df.dropna()
    df_null = df_nonan.sample(frac=frac,ignore_index=True)

    # Extract the subset as NumPy array
    arr = df_null[filters].to_numpy()

    # 1. Row-wise min value & index (ignoring NaNs)
    row_mins = np.nanmin(arr, axis=1)
    row_argmins = np.nanargmin(arr, axis=1)

    # 2. Compute shift k per row
    limiting_arr = np.array([limiting_mags[f] for f in filters])  
    row_limiting = limiting_arr[row_argmins]                      
    k = (row_limiting - np.random.uniform(2,4,len(row_mins))) - row_mins                             

    # 3. Shift all filters in one go
    arr = arr + k[:, None]

    # 4. Mask values dimmer than the limit
    mask = arr > limiting_arr[None, :]   # compare against col-wise limits
    arr[mask] = np.nan

    # Assign back
    df_null[filters] = arr

    df = pd.concat([df,df_null],ignore_index=True)

    return df


def add_null_bright(df, filters, saturating_mags=None, frac = 0.1):
    """ Add null values for some fraction of the data, where the null values are placed where the filter
    is brighter than the saturating magnitude of the observation. The saturating magnitude is determined
    by shifting the entire SED such that the brightest filter is 1-5 mags dimmer than the saturating mag.
    Inputs:
    df (DataFrame): The dataframe to which nulls will be added.
    filters (list): The filters to be used.
    saturating_mags (dict): The saturating magnitudes for each filter.
    frac (float): The fraction of the data to which nulls will be added.    
    
    Returns:
    df (DataFrame): The dataframe with nulls added."""

    if saturating_mags is None:
        raise ValueError("Must input saturation limiting mags of observation!")

    # Define new sample for nans
    df_nonan = df.dropna()
    df_null = df_nonan.sample(frac=frac,ignore_index=True)

    # Extract the subset as NumPy array
    arr = df_null[filters].to_numpy()

    # Row-wise minimums
    row_maxs = np.nanmax(arr, axis=1)
    row_argmaxs = np.nanargmax(arr, axis=1)

    # 2. Compute shift k per row
    limiting_arr = np.array([saturating_mags[f] for f in filters])  
    row_limiting = limiting_arr[row_argmaxs]   
    # The magnitude of the dimmest filter will be 3 magnitude mags dimmer than the saturation limit.                 
    k = (row_limiting + np.random.uniform(1,5,len(row_maxs))) - row_maxs                             

    # 3. Shift all filters in one go
    arr = arr + k[:, None]

    # 4. Mask values brighter than the limit
    mask = arr < limiting_arr[None, :]   # compare against col-wise limits
    arr[mask] = np.nan

    # Assign back
    df_null[filters] = arr

    df = pd.concat([df,df_null],ignore_index=True)

    return df

def add_null_random(df,filters,frac=0.3):
    """ Add null values for some fraction of the data, where the null values are placed randomly
    throughout the filters.
    Inputs:
    df (DataFrame): The dataframe to which nulls will be added.
    filters (list): The filters to be used.
    frac (float): The fraction of the data to which nulls will be added.
    
    Returns:
    df (DataFrame): The dataframe with nulls added."""

    arr = df[filters].to_numpy()
    n_rows, n_cols = arr.shape

    # Weighted probabilities for 0, 1, or 2 NaNs per row
    weights = [1-frac, frac*3/4, frac*1/4]  # adjust as you like
    n_nans_per_row = np.random.choice([0, 1, 2], size=n_rows, p=weights)

    # Row indices (repeated according to number of NaNs)
    row_idx = np.repeat(np.arange(n_rows), n_nans_per_row)

    # Column indices (different random cols for each row with >0 NaNs)
    col_idx = np.concatenate([
        np.random.choice(n_cols, k, replace=False) 
        for k in n_nans_per_row if k > 0
    ]) if row_idx.size > 0 else np.array([], dtype=int)

    # Apply NaNs
    arr[row_idx, col_idx] = np.nan

    # Assign back
    df[filters] = arr

    return df


def null_filter(df,filt,frac=0.1):
    df_null = df.sample(frac=frac).copy()
    df_null[filt] = np.nan

    df_null = pd.concat([df,df_null],ignore_index=True)
    return df_null


def oversample(df, n = 10000):
    """A simple function for oversampling all the classes in a dataframe to the same degree. 
    Takes as input a dataframe and returns a new dataframe with oversampled classes.
    NOTE: do not use prior to splitting data into training and validation as this will
    result in copies of the same rows.
    
    Inputs:
    df (DataFrame): The dataframe to be oversampled.
    n (int): The number of samples to which each class will be oversampled.
    
    Returns:
    df_new (DataFrame): The oversampled dataframe.
    """

    for label in np.unique(df.Class):
        df_l = df[df.Class==label].copy()
        df_l.reset_index(drop=True,inplace=True)
        df_l = pd.concat([df_l]*int(np.ceil(n/len(df_l))),ignore_index=True).reset_index(drop=True)
        
        # Intentionally do not oversample the brown and white dwarfs to keep these classes imbalanced.
        if (label == "WD") | (label == "BD"):
            rand_samp = random.sample(range(0,len(df_l[df_l.Class==label])),int(n/2))
        else:
            rand_samp = random.sample(range(0,len(df_l[df_l.Class==label])),n)

        try:
            df_new = pd.concat([df_l.loc[rand_samp].copy(),df_new])
        except:
            df_new = df_l.loc[rand_samp].copy()
    df_new = df_new.sample(frac=1).reset_index(drop=True)
    return df_new
        
def prep_all_dat(df_train, df_real, filters):
    """ Prepare all the data for training, validation, testing, and real classification. 
    Adds noise, nulls, colours, and splits the data.
    
    Inputs:
    df_train (DataFrame): The training dataframe.
    df_real (DataFrame): The real dataframe to be classified.
    filters (list): The filters to be used.
    
    Returns:
    df_train_new (DataFrame): The prepared training dataframe.
    df_val_new (DataFrame): The prepared validation dataframe.
    df_test_new (DataFrame): The prepared testing dataframe.
    df_real_new (DataFrame): The prepared real dataframe to be classified."""
    
    # Get rid of infinite values
    df_train_new = df_train.replace([np.inf, -np.inf], np.nan)
    df_real_new = df_real.replace([np.inf, -np.inf], np.nan)
    df_train_new.dropna(inplace=True,ignore_index=True)

    # Add noise to synthetic data
    df_train_new = add_noise(filters, df_train_new, df_real_new)

    # Add nulls to training and validation sets
    # Acquire limiting and saturating mags from real data
    limiting_mags = {f:np.nanquantile(df_real_new[f].values,0.99) for f in filters}
    saturating_mags = {f:np.nanquantile(df_real_new[f].values,0.01) for f in filters}
    # Choose 30% of the sample to fill with null values
    df_train_null = df_train_new.sample(frac=1,ignore_index=True) 
    # Split between null from out of frame or messy data; and saturated/undetected
    df_train_null_detectable, df_train_null_messy = train_test_split(df_train_null, train_size=0.75, random_state=700) 
    # Split evenly between saturation and undetected
    df_train_null_faint, df_train_null_bright = train_test_split(df_train_null_detectable, train_size=0.85, random_state=700) 
    # Replace with nulls based on limiting magnitude
    df_train_null_faint = add_null_faint(df_train_null_faint, filters, limiting_mags=limiting_mags, frac=1)
    # Replace with nulls based on saturating magnitude
    df_train_null_bright = add_null_bright(df_train_null_bright, filters, saturating_mags=saturating_mags, frac=1)
    # Deal with messy data now:
    # Take away random filters
    df_train_null_messy = add_null_random(df_train_null_messy,filters,frac=0.5)
    # Concatenate together (NOTE: we include the non-nulled rows to help the algorithm in training)
    df_train_new = pd.concat([df_train_null_faint, df_train_null_bright,df_train_null_messy],ignore_index=True).sample(frac=1,ignore_index=True)
    # For each filter, if there is a systematic missing amount of data not otherwise accounted for, we included further random nulls
    for f in filters:
        frac = len(df_real_new.loc[df_real_new[f].isna(),f])/len(df_real_new[f]) - len(df_train_new.loc[df_train_new[f].isna(),f])/len(df_train_new[f])
        if frac < 0:
            df_train_new = null_filter(df_train_new,f,frac=0.1)
            continue
        else:
            df_train_new = null_filter(df_train_new,f,frac=frac)


    # Get colours/other features
    df_train_new = add_fc(df_train_new.copy(),filters,train=True)
    df_real_new = add_fc(df_real_new.copy(),filters,train=False)
    df_train_new = df_train_new.replace([np.inf, -np.inf], np.nan)
    df_real_new = df_real_new.replace([np.inf, -np.inf], np.nan)

    
    # Split data
    df_train_new, df_val_new = train_test_split(df_train_new, train_size=0.75, random_state=700)
    df_val_new, df_test_new = train_test_split(df_val_new, train_size=0.5, random_state=700)
    

    # Oversample training set and finish prepping
    df_train_new = oversample(df_train_new)
    
    fcd_columns = [c for c in df_train_new.columns if ('-' in c) | ('/' in c) | c.startswith('PCA_')]
    df_train_new = df_train_new.replace([np.inf, -np.inf], np.nan)
    df_val_new = df_val_new.replace([np.inf, -np.inf], np.nan)
    df_test_new = df_test_new.replace([np.inf, -np.inf], np.nan)
    df_real_new = df_real_new.replace([np.inf, -np.inf], np.nan)
    

    return df_train_new, df_val_new, df_test_new, df_real_new





def add_fc(dao_fcd,filters,train=False):
    """Function for adding in colours for the specified filters. All filter combinations
    are returned."""
    if train:
        dao_fcd = dao_fcd.sample(frac=1).reset_index(drop=True)
    
    for f, filt in enumerate(filters):
        for filt2 in filters[f+1:]:
            col = filt+"-"+filt2
            dao_fcd[col] = dao_fcd[filt] - dao_fcd[filt2]
            
    return dao_fcd






def test_filters(filters, classes=['YSO', 'FS', 'WD', 'BD', 'Gal'], limiting_mags = None, saturating_mags = None, errs=None, threads = 1):
    """ This function is for testing filter choices for JWST proposals. Specifically, it is used to determine
    what the best performance of SESHAT will be with those filters. 
    
    Inputs:
    filters (list): The filters to be tested.
    classes (list): The classes to be identified.
    limiting_mags (dict): The limiting magnitude for each filter in filters.
    saturating_mags (dict): The saturating magnitude for each filter in filters.
    errs (2D list): The error distribution for each filter in filter.
    threads (int): The number of threads to use when classifying.

    Returns:
    test (DataFrame): A pandas DataFrame containing the true classes, the predicted classes, as well as the predicted probabilities for the test set.
    """
    

    fake_test = pd.DataFrame()

    if (limiting_mags is None) | (saturating_mags is None):
        raise Exception("Must include limiting and saturating magnitudes!")
    
    if (errs is None):
        raise Exception("Must include errors!")
    
    for i, f in enumerate(filters):
        mags = np.random.uniform(high=limiting_mags[f],low=saturating_mags[f],size=np.shape(errs)[1])
        fake_test[f] = mags
        fake_test['e_'+f] = errs[i][:]

    _, test, _ = classify(real=fake_test,classes=classes,threads=threads,return_test=True)

    return test