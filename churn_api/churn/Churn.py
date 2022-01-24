import pandas as pd
import pickle, json

class churnEvaluation( object ):
    def __init__(self): #, preprocessing_pipe, model_pipe

        # defining preprocessing pipeline
        prepr_path = 'features/'
        self.preprocessing_pipe = pickle.load( open( prepr_path + 'preprocessing_pipe.pkl', 'rb') )

        # defining model pipeline
        model_path = 'models/'
        self.model_pipe = pickle.load( open( model_path + 'model_pipe.pkl', 'rb') )

    # Preprocessing
    def preprocessing( self, X_test):
        # droping cols
        X_test = X_test.drop(columns = [ 'row_number', 'customer_id', 'surname', 'num_of_products' ], axis = 1).copy()
        X_test_t = self.preprocessing_pipe.transform( X_test )
        return X_test_t

    # Predicting
    def predicting( self, X_test_t):

        # making the prediction
        y_score = self.model_pipe.predict_proba(X_test_t)
        return y_score

    # Returning prediction + LTV
    def compose_result( self, X_test_raw, y_score):
        res = X_test_raw.copy()
        res['churn_proba'] = y_score[:,1]

        per_balance = 0.08
        per_salary = 0.05
        res['ltv'] = res.apply( lambda x: x['balance']*per_balance + x['salary']*per_salary, axis = 1 )

        return res.to_json( orient = 'records' )
