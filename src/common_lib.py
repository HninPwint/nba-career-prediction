#A module to read raw data from source for further analysis.
#Data are stored in the raw_data folder for the original dataset and processed_data for the cleaned dataset.

from enum import Enum
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler, PolynomialFeatures

from imblearn.over_sampling import SMOTE

class NBARawData(Enum):
    '''List of members to identify the name of each dataset stored in the raw_data folder.
       One enumerator member represents one file in the folder.
    '''
    TRAIN = 0
    TEST = 1

class DataReader:
    def __init__(self, relative_path = "../"):
    

        self.filepath = {}
        #raw data
        self.filepath.update({NBARawData.TRAIN : relative_path + "data/raw/train.csv"})
        self.filepath.update({NBARawData.TEST : relative_path + "data/raw/test.csv"})

   
    def read_data(self, source, relative_path = "../"):
        '''Read the CSV file and load it into a data frame.
        
           Argument:
               source (enum): the member name of the dataset that will be loaded, e.g., NBARawData.TRAIN 
           
           Return:
               a data frame that store the dataset
        '''
        if (not isinstance(source,NBARawData)):
            raise Exception("argument should be filled with NBARawData "
                            "Try NBARawData.TRAIN and/or NBARawData.TEST")
            
        #read the data and load them into a dataframe
        data = pd.read_csv(self.filepath[source])
        #for consistency purposes, change the case of the column names into a lower case and remove extra spaces
        data = data.rename(columns = lambda x: x.strip(" "))
        return(data)

    def split_data(self, data, relative_path = "../"):
        data = pd.DataFrame(data)
        target = data.pop('TARGET_5Yrs')
        X_train, X_val, y_train, y_val = train_test_split(data, target, test_size = 0.2, random_state=8, shuffle=True )

        # Save the splited data
        np.save(relative_path+ "data/processed/X_train", X_train)
        np.save(relative_path+ "data/processed/X_train", X_val)

        np.save(relative_path+ "data/processed/X_train", y_train)
        np.save(relative_path+ "data/processed/X_train", y_val)
        return(X_train, X_val, y_train, y_val)

    def select_feature_by_correlation(self, data, columns_to_drop):
        '''This function select the features according to the correlation result.
            The features which have correlation > 0.9 are filter out.
        '''
        
        data.drop(columns_to_drop, axis=1, inplace=True )
        corr = data.corr()
        sns.heatmap(corr)

        columns = np.full((corr.shape[0],), True, dtype=bool)
        for i in range(corr.shape[0]):
            for j in range(i+1, corr.shape[0]):
                if corr.iloc[i,j] >= 0.9:
                    if columns[j]:
                        columns[j] = False
        selected_columns = data.columns[columns]
        return selected_columns

    
    def scale_features_by_standard_scaler(self, df):
        '''
        '''
    

        scaler = StandardScaler()
        df_scaled = scaler.fit_transform(df)
        
        # Set as pd.dataframe and Re-apply column names and
        scaled_df = pd.DataFrame(df_scaled)
        scaled_df.columns = df.columns
        return scaled_df
    
    def polynomialize_data(self, df, degree):
        '''
        '''
        # Polynomialise
        poly = PolynomialFeatures(degree)
        data_poly = poly.fit_transform(df)
        
        data_poly = pd.DataFrame(data_poly)
        # data_poly.columns = df.columns
        return data_poly
        
    
    def plot_class_balance(self, df):
        '''
        '''
        
        pl = pd.DataFrame(df)
        pl.columns = ['Target']
        pl.Target.value_counts().plot(kind="bar", title="Count Target")
        
    def resample_data_upsample_smote(self, X, y):
        '''
        '''
        
        sm = SMOTE(random_state = 23, sampling_strategy = 1.0)
        X_res, y_res = sm.fit_resample(X, y.ravel())
        return( X_res, y_res)
    
    def clean_negatives(self, strategy, df):
        '''
        # Negative values do not make sense in this context
        # Define negative cleaning function
        # Pass any other string to retain negatives
        '''
    
        if strategy=='abs':
            df = abs(df)
        if strategy=='null':
            df[df < 0] = None
        if strategy=='mean':
            df[df < 0] = None
            df.fillna(df.mean(), inplace=True)     
        if strategy=='median':
            df[df < 0] = None
            df.fillna(df.median(), inplace=True) 

        return(df)

# end of DataReader


def confusion_matrix(true, pred):
    # Confusion matrix with labels

    import numpy as np
    import pandas as pd
    from sklearn import metrics

    unique_label = np.unique([true, pred])
    cmtx = pd.DataFrame(
        metrics.confusion_matrix(true, pred, labels=unique_label), 
        index=['true:{:}'.format(x) for x in unique_label], 
        columns=['pred:{:}'.format(x) for x in unique_label]
    )
    return(cmtx)

def plot_roc(y_true, y_pred):

    from sklearn.metrics import roc_curve, auc
    import matplotlib.pyplot as plt

    fpr, tpr, thresh = roc_curve(y_true, y_pred)
    roc_auc = auc(fpr, tpr)
    print('AUC = %0.3f' % roc_auc)
    plt.plot(fpr, tpr, 'b', label='AUC = %0.3f' % roc_auc)
    plt.plot([0,1],[0,1], 'r--')
    plt.xlim([-0.1,1.0])
    plt.xlim([-0.1,1.01])
    return(plt)

def eval_report(true, pred):

    import numpy as np
    import pandas as pd
    from sklearn import metrics

    unique_label = np.unique([true, pred])
    cmtx = pd.DataFrame(
        metrics.confusion_matrix(true, pred, labels=unique_label), 
        index=['true:{:}'.format(x) for x in unique_label], 
        columns=['pred:{:}'.format(x) for x in unique_label]
    )
    print("Confusion Matrix:")
    print(cmtx)
    print("")
    print("Classification Report:")
    print(metrics.classification_report(true, pred))
    print("")
    print("ROC Curve:")

    import matplotlib.pyplot as plt  
    plot_roc(true, pred)
    plt.show()
