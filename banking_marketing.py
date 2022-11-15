# -*- coding: utf-8 -*-
"""Banking Marketing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Go9bvlN7jMeOaHbmcVuNrYGzODS53uU0

# Import Libraries
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pandas.plotting import scatter_matrix
pd.set_option('display.max_columns', 999)
# %matplotlib inline

"""## Load Dataset"""

bank = pd.read_csv('/bank-additional-full.csv', sep = ";")
bank.head(5)

"""# Dimensions of Dataset and Structure"""

bank.columns

#change the columns name y to deposit
bank = bank.rename(index=str, columns={"y": "deposit"})

bank.shape

bank.dtypes

"""# Statistical Summary and Correlation Matrix Graph"""

bank.describe()

"""#### The numerical values have the different scale or different range.  We might need to standardize the data or normalizethe data to improve the accuracy."""

bank.corr()

"""#### The correlation matrix is little hard to read.  Let's plot it."""

#filter out the numerical variables and categorical variables
num_colmuns = []
cat_columns = []
for name, type in dict(bank.dtypes).items():
        if type =='int64' or type == 'float64':
            num_colmuns.append(name)
        else:
            cat_columns.append(name)

#fig.add_subplot(nrows, ncols, plot_number)
fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(1,1,1)
cax = ax.matshow(bank.corr(), vmin=-1, vmax=1)
fig.colorbar(cax)
ticks = np.arange(0,10,1)
ax.set_xticks(ticks)
ax.set_yticks(ticks)
ax.set_xticklabels(num_colmuns, rotation = 45)
ax.set_yticklabels(num_colmuns)

"""#### Based on the correlation plot:
* nr.employed and euribor3m are highly positive correlated.
* nr.employed and emp.var.rate are highly positive correlated.
* euribor3m and emp.var.rate are highly positive correlated.

### Histogram of Numerical Variables
"""

num_colmuns

fig = plt.figure(figsize=(18,18))
for r in range(0,10):
    ax = fig.add_subplot(5,2,r+1)
    ax = bank[num_colmuns[r]].hist()
    ax.set_xlabel(num_colmuns[r])

"""### Bar Plot of Categorical Variables"""

cat_columns[0:10]

fig = plt.figure(figsize=(25,46))
for r in range(0,10):
    ax = fig.add_subplot(5,2,r+1)
    ax = bank[cat_columns[r]].value_counts().plot(kind = 'bar', rot=35, fontsize = 13)
    ax.set_xlabel(cat_columns[r],fontsize = 20)
    ax.xaxis.set_label_coords(1.05, -0.025)
    ax.set_ylabel('counts')

"""### Plot the Target Variable"""

# Set figure size with matplotlib
fig, axs = plt.subplots(1,2,figsize=(14,7))
#create the frequency graph of Target variable deposit
sns.countplot(x='deposit',data=bank, ax=axs[0])
axs[0].set_title("Frequency of each Term Deposit Status")
#create the pie graph of Target variable deposit in term of percentage
bank.deposit.value_counts().plot(x=None,y=None, kind='pie', ax=axs[1],autopct='%1.3f%%')
axs[1].set_title("Percentage of each Term Deposit Status")

"""# Data Preprocessing / Preparing Features for Machine Learning

### Check the Missing Values
"""

null_counts = bank.isnull().sum()
print("Number of null values in each column:\n{}".format(null_counts))

print("Data types and their frequency\n{}".format(bank.dtypes.value_counts()))

"""### Preparing for Categorical Variables / Convert Categorical Variables to Numeric Features

* ####   Map Ordinal Values To Integers
* ####   Encode Nominal Values as Dummy Variables
"""

object_columns_df = bank.select_dtypes(include=['object'])
print(object_columns_df.iloc[0])

#we need to drop columns month and day_of_week
bank_prepared = bank.drop(['month', 'day_of_week'], axis = 1)

#deposit is Target Variable
cols = ['job', 'marital', 'education', 'default', 'housing','loan', 'contact', 'poutcome']
for name in cols:
    print(name,':')
    print(bank_prepared[name].value_counts(),'\n')

"""#### Nominal Levels:
* job

* marital

* default

* housing

* loan

* contact

* poutcome


#### Ordinal Levels:
* education

"""

#Nomial
Nominal = ['job','marital', 'default', 'housing', 'loan', 'contact', 'poutcome']
dummies = pd.get_dummies(bank[Nominal])

bank_prepared = pd.concat([bank_prepared, dummies],axis=1)
bank_prepared = bank_prepared.drop(Nominal, axis = 1)


#Ordinal
bank_prepared['education'] = bank_prepared['education'].replace(['basic.4y','basic.6y','basic.9y'], 'basic')

mapping_dict = {
    "education": {
        "university.degree": 5,
        "professional.course": 4,
        "basic": 3,
        "high.school": 2,
        "illiterate": 1,
        "unknown": 0
    }
}
bank_prepared = bank_prepared.replace(mapping_dict)

"""### Preparing for Numerical Variables
* Input variable duration is highly affect the target variables.  Therefore, I will remove it.
"""

bank_prepared = bank_prepared.drop(['duration'], axis = 1)

"""### Preparing for Target Variable"""

bank_prepared['deposit'] = bank_prepared['deposit'].map(dict(yes=1, no=0))

bank_prepared['deposit'].value_counts()

"""# Machine Learning"""

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, KFold, cross_val_score,GridSearchCV
from sklearn.metrics import roc_auc_score, confusion_matrix,precision_score, recall_score, accuracy_score,classification_report,roc_curve,f1_score    
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier, RandomForestClassifier, ExtraTreesClassifier
from sklearn.model_selection import cross_val_predict
from sklearn.utils import resample
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline, FeatureUnion

"""### Split the data into 80% training and 20% testing"""

validation_size = 0.20
seed = 10
bank_train, bank_test = train_test_split(bank_prepared, test_size=validation_size, random_state=seed)

X_train = bank_train.drop(['deposit'], axis = 1)
Y_train = bank_train['deposit']
X_test = bank_test.drop(['deposit'], axis = 1)
Y_test = bank_test['deposit']

Y_train.value_counts(normalize = True)

Y_test.value_counts(normalize = True)

"""## Training Machine Learning Model on Imbalanced Data
* Logistics Regression
* KNN
* Decision Tree
* Naive Bayes

### Using 10 Fold Cross Validation
* Accuracy
* Recall
* Precision
* ROC - Area Under ROC Curve
"""

# Spot Check Algorithms
models = []
models.append(('Logistic Regression', LogisticRegression()))
models.append(('KNN', KNeighborsClassifier()))
models.append(('Decision Tree', DecisionTreeClassifier()))
models.append(('Naive Bayes', GaussianNB()))
results = []
names = []
roc = []
for name, model in models:
    cv_results = cross_val_score(model, X_train.values, Y_train.values, cv = 10, scoring = 'accuracy')
    y_train_pred = cross_val_predict(model, X_train.values, Y_train.values, cv = 10)
    roc_results = cross_val_score(model, X_train.values, Y_train.values, cv=10, scoring = 'roc_auc')
    results.append(cv_results)
    names.append(name)
    roc.append(roc_results)
    print("{}\nAccuracy: {:.4f}({:.4f})".format(name, cv_results.mean(), cv_results.std()))
    print("Recall: {:.4f}".format(recall_score(Y_train.values, y_train_pred)))
    print("Precision: {:.4f}".format(precision_score(Y_train.values, y_train_pred)))
    print("ROC: {:.4f}".format(roc_results.mean()))
    print('confusition_matrix')
    print(confusion_matrix(Y_train.values, y_train_pred))
    print('------------------------------------------------')
    print("\n")

"""#### It looks like imbalance target variable affect the model performance.   The models are biased and will predict as 0 most of time. Models will ignore the minority class in favor of the majority class. We need to balance the target variable."""

bank_train['deposit'].value_counts()

"""## Upsampled to adjust the imbalanced data"""

# Separate majority and minority classes
bank_majority = bank_train[bank_train['deposit']==0]
bank_minority = bank_train[bank_train['deposit']==1]
 
# Upsample minority class
bank_minority_upsampled = resample(bank_minority, 
                                 replace = True,     # sample with replacement
                                 n_samples = 29238,# to match majority class
                                 random_state=10) # reproducible results
 
# Combine majority class with upsampled minority class
bank_upsampled = pd.concat([bank_majority, bank_minority_upsampled],axis=0)
 
# Display new class counts
bank_upsampled['deposit'].value_counts()

"""## Train Machine Learning Model on Balanced Data 
* Logstics Regression
* KNN
* Decision Tree
* Navie Bayes
"""

X_train_bal = bank_upsampled.drop(['deposit'], axis = 1)
Y_train_bal = bank_upsampled['deposit']
# Spot Check Algorithms
models_ = []
models_.append(('Logistic Regression', LogisticRegression()))
models_.append(('KNN', KNeighborsClassifier()))
models_.append(('Decision Tree', DecisionTreeClassifier()))
models_.append(('Naive Bayes', GaussianNB()))
results_ = []
names_ = []
roc_ = []
for name, model in models_:
    cv_results_ = cross_val_score(model, X_train_bal.values, Y_train_bal.values, cv = 10, scoring = 'accuracy')
    y_train_pred_ = cross_val_predict(model, X_train_bal.values, Y_train_bal.values, cv = 10)
    results_.append(cv_results_)
    names_.append(name)
    print("{}\nAccuracy: {:.4f}({:.4f})".format(name, cv_results_.mean(), cv_results_.std()))
    print("Recall: {:.4f}".format(recall_score(Y_train_bal.values, y_train_pred_)))
    print("Precision: {:.4f}".format(precision_score(Y_train_bal.values, y_train_pred_)))
    print('confusition_matrix')
    print(confusion_matrix(Y_train_bal.values, y_train_pred_))
    print('------------------------------------------------')
    print("\n")

"""#### Decision Tree performed the best with over 94 percent accuracy among these four.

"""

num_colmuns

columns = list(bank_upsampled)
columns.remove('deposit')
num_colmuns.remove('duration')

cat_list_feature = []
num_list_feature = []
for i in columns:
    if i not in num_colmuns:
        cat_list_feature.append(i)
    else:
        num_list_feature.append(i)

# Create a class to select numerical or categorical columns 
# since Scikit-Learn doesn't handle DataFrames yet
class DataFrameSelector(BaseEstimator, TransformerMixin):
    def __init__(self, attribute_names):
        self.attribute_names = attribute_names
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        return X[self.attribute_names].values

num_pipeline = Pipeline([
        ('selector', DataFrameSelector(num_list_feature)),
        ('standardized', StandardScaler())
    ])

cat_pipeline = Pipeline([
        ('selector', DataFrameSelector(cat_list_feature))
    ])

full_pipeline = FeatureUnion(transformer_list=[
        ("num_pipeline", num_pipeline),
        ("cat_pipeline", cat_pipeline),
    ])

X_train_scaled = full_pipeline.fit_transform(bank_upsampled)

# Spot Check Algorithms
models__ = []
models__.append(('Logistic Regression Scaled', LogisticRegression()))
models__.append(('KNN Scaled', KNeighborsClassifier()))
models__.append(('Decision Tree Scaled', DecisionTreeClassifier()))
models__.append(('Naive Bayes Scaled', GaussianNB()))
results__ = []
names__ = []
roc__ = []

for name, model in models__:
    cv_results__ = cross_val_score(model, X_train_scaled, Y_train_bal.values, cv = 10, scoring = 'accuracy')
    y_train_pred__ = cross_val_predict(model, X_train_scaled, Y_train_bal.values, cv = 10)
    results__.append(cv_results__)
    names__.append(name)
    print("{}\nAccuracy: {:.4f}({:.4f})".format(name, cv_results__.mean(), cv_results__.std()))
    print("Recall: {:.4f}".format(recall_score(Y_train_bal.values, y_train_pred__)))
    print("Precision: {:.4f}".format(precision_score(Y_train_bal.values, y_train_pred__)))
    print('confusition_matrix')
    print(confusion_matrix(Y_train_bal.values, y_train_pred__))
    print('------------------------------------------------')
    print("\n")

# Spot Check Algorithms
ensembles = []
ensembles.append(('Ada Boost', AdaBoostClassifier()))
ensembles.append(('Gradient Boosting Machine', GradientBoostingClassifier()))
ensembles.append(('Random Forest', RandomForestClassifier()))

results___ = []
names___  = []
for name, model in ensembles:
    cv_results___ = cross_val_score(model, X_train_scaled, Y_train_bal.values, cv = 10, scoring = 'accuracy')
    y_train_pred___ = cross_val_predict(model, X_train_scaled, Y_train_bal.values, cv = 10)
    results___.append(cv_results___)
    names___.append(name)
    print("{}\nAccuracy: {:.4f}({:.4f})".format(name, cv_results___.mean(), cv_results___.std()))
    print("Recall: {:.4f}".format(recall_score(Y_train_bal.values, y_train_pred___)))
    print("Precision: {:.4f}".format(precision_score(Y_train_bal.values, y_train_pred___)))
    print('confusition_matrix')
    print(confusion_matrix(Y_train_bal.values, y_train_pred___))
    print('------------------------------------------------')
    print("\n")

"""## Random Forest Tuning"""

#using grid search for tuning parameters
param_grid = [
        {'n_estimators': [200,500], 
         'max_features': [4, 6, 8]}
]
bank_RF = RandomForestClassifier(n_jobs=-1, random_state=42)
#using 5 fold, because it's faster to train.
grid_search = GridSearchCV(bank_RF, param_grid, cv = 5)
grid_search.fit(X_train_scaled, Y_train_bal.values)

#print best parameters
grid_search.best_params_

grid_search.best_estimator_

cv_clf = grid_search.cv_results_
for mean_score, params in zip(cv_clf["mean_test_score"], cv_clf["params"]):
    print(mean_score.mean(), params)

"""#### The best parameter for max_features is 8 and best parameter for n_estimators is 200"""

#train Random Forest using those parameters
best_model = grid_search.best_estimator_
X_test_scaled = full_pipeline.fit_transform(X_test)
final_predictions = best_model.predict(X_test_scaled)
final_accuracy = accuracy_score(Y_test.values,final_predictions)
Recall = recall_score(Y_test.values,final_predictions)
Precision = precision_score(Y_test.values,final_predictions)
F1_Score = f1_score(Y_test.values,final_predictions)
acu_score = roc_auc_score(Y_test.values,final_predictions)
print("Final_Accuracy: {:.4f}".format(final_accuracy))
print("Recall: " + str(Recall))
print("Recall: " + str(Precision))
print("Recall: " + str(F1_Score))
print("acu_area: " + str(acu_score))

"""### Confusion Matrix"""

confusion_matrix(Y_test.values,final_predictions)

