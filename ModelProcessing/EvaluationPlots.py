from datetime import date
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from sklearn.metrics import roc_curve, auc, precision_recall_curve



class LiftGainChart:

    def __init__(self, y_true, probas):

        self.y_true = y_true
        self.probas = probas
        self.Charts()

    
    def CreateDeciles(self):

        decile = pd.DataFrame(self.probas, columns=['SCORE'])
        decile['DECILE'] = pd.qcut(decile['SCORE'].rank(method='first'), 10, labels=[10,9,8,7,6,5,4,3,2,1])
        decile['DECILE'] = decile['DECILE'].astype(float)
        decile['TARGET'] = self.y_true
        decile['NONTARGET'] = 1 - self.y_true
        return decile


    @staticmethod    
    def plots(agg1, target, type):

        plt.figure(1, figsize=(20, 5))
        plt.subplot(131)
        plt.plot(agg1['DECILE'], agg1['ACTUAL'], label='Actual')
        plt.plot(agg1['DECILE'], agg1['PRED'], label='Pred')
        plt.xticks(range(10, 110, 10))
        plt.legend(fontsize=15)
        plt.grid(True)
        plt.title('Actual vs. Predicted', fontsize=20)
        plt.xlabel('Population %', fontsize=15)
        plt.ylabel(str(target) + ' ' + str(type) + ' %', fontsize=15)

        plt.subplot(132)
        X = agg1['DECILE'].to_list()
        X.append(0)
        Y = agg1['DIST_TAR'].to_list()
        Y.append(0)
        plt.plot(sorted(X), sorted(Y))
        plt.plot([0, 100], [0, 100], 'r--')
        plt.xticks(range(0, 110, 10))
        plt.yticks(range(0, 110, 10))
        plt.grid(True)
        plt.title('Gains Chart', fontsize=20)
        plt.xlabel('Population %', fontsize=15)
        plt.ylabel(str(target) + ' Distribution %', fontsize=15)

        plt.subplot(133)
        plt.plot(agg1['DECILE'], agg1['LIFT'])
        plt.xticks(range(10, 110, 10))
        plt.grid(True)
        plt.title('Lift Chart', fontsize=15)
        plt.xlabel('Population %', fontsize=15)
        plt.ylabel('Lift', fontsize=15)
        plt.tight_layout()


    def Charts(self):

        data = self.CreateDeciles()
        inputs = list(['DECILE'])
        inputs.extend(('TARGET','SCORE'))

        decile = data[inputs]
        grouped = decile.groupby(['DECILE'])
        agg1 = pd.DataFrame({}, index=[])
        agg1['ACTUAL'] = grouped.mean()['TARGET']*100
        agg1['PRED']   = grouped.mean()['SCORE']*100
        agg1['DIST_TAR'] = grouped.sum()['TARGET'].cumsum()/grouped.sum()['TARGET'].sum()*100
        agg1.index.name = 'DECILE'
        agg1.reset_index(inplace=True)
        agg1['DECILE'] = agg1['DECILE']*10
        agg1['LIFT'] = agg1['DIST_TAR']/agg1['DECILE']

        self.plots(agg1, 'TARGET', 'Distribution')



class BuildROCandPrecisionRecall:

    def __init__(self, y_true, probas):

        self.y_true = y_true
        self.probas = probas
        self.Plot()

    
    def Build_ROC(self):

        fpr, tpr, threshold = roc_curve(self.y_true, self.probas)
        roc_auc = auc(fpr, tpr)

        plt.title('Receiver Operating Characteristic')
        agg1 = pd.DataFrame({}, index=[])
        agg1['FPR'] = fpr
        agg1['TPR'] = tpr

        plt.plot(fpr, tpr, label='AUC = %0.2f' % roc_auc)
        plt.legend(loc='lower right')
        plt.plot([0, 1], [0, 1], 'r--')
        plt.ylabel('True Positive Rate')
        plt.xlabel('False Positive Rate')
        plt.grid(True)


    def Build_Precision_Recall(self):

        precision, recall, threshold = precision_recall_curve(self.y_true, self.probas)
        F1 = 2*(precision*recall)/((precision + recall))
        plt.title('Precision & Recall Curve')
        plt.plot(recall, precision)
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.ylim((0, 1))
        plt.xlim((0, 1))
        plt.grid(True)


    def Plot(self):
        plt.figure(figsize=(12,8))
        plt.subplot(1, 2, 1)
        self.Build_ROC()
        plt.subplot(1, 2, 2)
        self.Build_Precision_Recall()
        plt.tight_layout()
