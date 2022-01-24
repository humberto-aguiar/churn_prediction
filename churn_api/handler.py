from flask import Flask, request, Response
import pandas as pd 
import os
from  churn.Churn import churnEvaluation

app = Flask (__name__ )
#app.run(debug=True)

@app.route( '/churn/predict', methods = ['POST'] )
def predict():

    # recieving data
    test_json = request.get_json()
  
    if test_json: # data recieved
        if isinstance( test_json, dict ): # single observation
            raw_data = pd.DataFrame( test_json, index = [0] )
        
        else: # multiple observations
            raw_data = pd.DataFrame( test_json, columns = test_json[0].keys() )
            
        # instatiating churnEvaluation class
        churn = churnEvaluation()
        
        # preprocessing data
        X_test_t = churn.preprocessing(raw_data)
        
        # making predictions
        y_score = churn.predicting( X_test_t )

        # composing result = raw_data + churn_proba + LTV
        res = churn.compose_result(raw_data, y_score)

    return res

#app.run( host='0.0.0.0' )
if __name__ == '__main__':
    port = os.environ.get("PORT", 5000)
    app.run(host = '0.0.0.0', port = port ) #debug = True