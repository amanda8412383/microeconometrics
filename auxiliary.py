
"""This module contains auxiliary functions for the creation of tables in the main notebook."""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.simplefilter("ignore")
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import statsmodels.api as sm
df = pd.read_stata('prune.dta')


def grouping(row):
    """create column to use in groupby"""
    if row['Conly'] == 1:
        return 'Condom only'
    elif row['CV'] == 1:
        return "Condom and VCT"
    elif row['VCTonly'] == 1:
        return "VCT only"
    elif row ['CVcontrol'] == 1:
        return "Control"

df['group'] = df.apply (lambda row: grouping(row), axis=1)
#filter out irrelavant or problematic entries
df_filter =  df.query('surveyed == 1 & ~group.isnull() & LOG_comments == "" & TRACKED == 1')

### generating / formatting variables columns needed in table 1
def cutting(incol, binwidth, labelname, pre_varname):
    """fct to group and create dummies for some continuos grouping v.s."""
    outcol = pd.cut(incol, bins = binwidth, labels=labelname, right = True, include_lowest = True)
    outcol = pd.get_dummies(outcol, prefix = pre_varname)
    return outcol

age = cutting(df_filter['age2009'], [17, 18, 20, 22, 24], ('<19', '19-20', '21-22', '>22'), 'Age at baseline')

#edulevel phase1
#the value is different from an_years_educ
edu = cutting(df_filter['Q_b1_13_school_years'], [6, 9, 11, 13, 20], ('<10', '10-11', '12-13', '>13'), 'Total year of schooling')
#enrolled phase1
df_filter['Not enrolled in school'] = 1 - df_filter['an_in_school']

#HSV phase1
df_filter['HSV-2 positive'] = np.where(df_filter['hsv2_positive'] == 1, 1, 0)

#married at phase 1
df_filter['Currently married'] = np.where(-df_filter['an_spouse_age'].isna(), 1, 0)

#sum up all ever pregnant records, children record, and tracked result
df_filter['Ever or partner ever pregnant'] = np.where(
    ((df_filter['evpreg07v2'] == 1 )| (df_filter['Track_children_number'] > 0) | (df_filter['Track_pregnant'] == "Yes" )),
      1, 0)

#condem latest intercourse phase1, ans have yes no notsure
df_filter['Last sex used condom'] = np.where(df_filter['Q_b4_127_last_sex_use_condom'] == 1, 1, 0)

#current likelihood be infected, ans 1 = not likely
df_filter['Believed current HIV infection'] = np.where(df_filter['Q_b3_99'] != 1, 1, 0)

#future likelihood be infected, ans 1 = not likely
df_filter['Believed future HIV infection'] = np.where(df_filter['Q_b3_100'] != 1, 1, 0)

#rename v.s. to be readable in table
df_filter = df_filter.rename(columns={"an_everhadsex": "Ever had sex", "an_multiplepartners": "Ever had multiple partners", 
                            "an_everHIVtested" : "Ever tested for HIV"})

#name at least 3 way to prevent hiv
prevent = df_filter.filter(regex='^an_Q_b3_80',axis=1).apply(sum, axis = 1)
df_filter['Named 3 prevention'] = np.where(prevent >= 3, 1, 0)

#answer at least 3 hiv related question correctly
correct = df_filter.filter(items=['an_Q_b3_83', 'an_Q_b3_84'],axis=1).apply(sum, axis = 1)
df_filter['Answered 3 questions'] = np.where((correct == 2) & (df_filter['an_Q_b3_88'] == 0), 1, 0)

#sum positive attitude answers
pos = df_filter.filter(regex='an_Q_b3_1.+([0-1]|9)_agree_with_statement',axis=1).apply(sum, axis = 1)
df_filter['Showed positive attitude'] = np.where((pos == 0 ) & (df_filter['an_Q_b3_112_agree_with_statement'] == 1), 1, 0)

df_merge = df_filter.join(age).join(edu)

def t1_component(df, varlist):
    """function for applying all criteria required in Table 1

    Args:
    ------
    data(pd.DataFrame): Dataset containing all data
    varlist: list containing string of interested variables

    Returns:
    ---------
    series(pd.series): dictionaries of name in variable list and computed values as key to a series"""
    dict = {}

    for i in range(len(varlist)):
        if i == 0:
            dict[varlist[i]] = df['pupilid'].nunique()
        else:
            dict[varlist[i]] = df[df[varlist[i]].values == 1 ]['pupilid'].nunique()
    return pd.Series(dict)

def table1(df, varlist):
    """ one-time function to assemble table 1 and make main notebook look cleaner
    Args:
    ------
    data(pd.DataFrame): Dataset containing all data
    varlist: list containing string of interested variables
    
    Returns:
    ---------
    table(pd.DataFrame): Dataframe containing 3 panel with summin statistic in varlist
    """
    #apply for all 3 categories
    total = df.groupby(["group"]).apply(t1_component, varlist=varlist)
    woman = df[df['sex'].values == '2 Female'].groupby(["group"]).apply(t1_component, varlist=varlist)
    man = df[df['sex'].values == '1 Male'].groupby(["group"]).apply(t1_component, varlist=varlist)

    #combine results
    table1 = pd.concat([total, woman, man], keys=['all', 'woman', 'man']).T
    
    return table1

def adjusted_odds_ratio(df_merge, var, treat):
    """ function to calculate adjusted odd ratio
    Args:
    ------
    data(pd.DataFrame): Dataset containing all data
    varlist: interested variables
    treat: string suggest treatment arm
    
    Returns:
    ---------
    adjusted odd ratio 
    ci: confidence interval formating as string
    """
    #prevent no value
    if df_merge[var].sum() <= 0:
        return 0, '(0-0)'
    #var as in paper

    df_s = df_merge[[var, 'weight_sample', treat, 'Age at baseline_<19', 'Age at baseline_19-20', 'Age at baseline_21-22', 
           'an2_female', 'an_in_school', 'evpreg07v2', 'month_diff']]
    #deal with na
    df_dropna = df_s.dropna()
    #regression
    X = sm.add_constant(df_dropna.iloc[ : , 2 : ])
    weight = np.array(df_dropna.weight_sample)
    y = df_dropna.iloc[ : ,  0]
    # Hessian might not be positive definite when far away from the optimum and raise singular matrix error
    #increase maxiter to fix Warning: Maximum number of iterations has been exceeded.
    reg = sm.Logit(y, X, sample_weight = weight).fit(method='bfgs', maxiter=100, disp=False)
    #getting values of interset
    par = reg.params
    aor = round(np.exp(par)[1], 2)
    ci = reg.conf_int(alpha=0.05, cols=None).iloc[1, :].apply(np.exp)
    ci_string = f'({ci[0]:.2f} - {ci[1]:.2f})'
    return aor, ci_string

#feeding group into adjusted_odds_ratio and return usable format
group_dict = {'Control': 'CVcontrol', 'Condom and VCT' : 'CV' , 'Condom only': 'Conly', 'VCT only': 'VCTonly'}

def framing_aor_ci(df_merge, var):
    """ formating aor and ci for each treatment of one variable into list, for producing data frame in next step
    Args:
    ------
    data(pd.DataFrame): Dataset containing all data
    var:  interested variables
    
    Returns:
    ---------
    indexlist: indicating order of the treatments in the following list
    aorlist : adjusted odd ratio as an ordered list 
    cilist: confidence interval formating as stringas an ordered list 
    """
    indexlist = []
    aorlist = []
    cilist = []
    for i in group_dict.keys():
        #ruling out control has no aoi, since it's the base group
        if i == 'Control':
            aor, ci = None, None      
        else:
            aor, ci = adjusted_odds_ratio(df_merge, var, group_dict[i])
        indexlist.append(i)
        aorlist.append(aor)
        cilist.append(ci)
    return indexlist, aorlist, cilist
        
def T2_component(df_merge, var, base):
    """ this fct calculate components use in a raw, used in table 2
    Args:
    ------
    data(pd.DataFrame): Dataset containing all data
    var:  interested variables
    base: denominator for interested variable
    
    Returns:
    ---------
    table(pd.DataFrame): Dataframe with 5 components as column, group as row index

    """
    #1 weighted sum of variable by group
    df_merge['Weighted cases'] = round(df_merge[var] * df_merge['weight_sample']* df_merge['sampleweight_clean'], 0)
    weighted_byg = df_merge.groupby(['group'])['Weighted cases'].sum()
    
    #2 weighted sum of variable's base by group
    num_byg = df_merge[~df_merge[base].isnull()].groupby(['group'])['pupilid'].nunique()
    #2-title sum of variable's base 
    n = num_byg.sum()    
    
    #3 ratio of 1 & 2
    #trans type for cauculation
    result = pd.concat([weighted_byg, num_byg], axis = 1) 
    result['Weighted%'] = round(result.iloc[:, 0] / result.iloc[:, 1] * 100, 2)
    
    #formatting 2
    n_string = f'N = {n}'
    result = result.rename(columns={'pupilid': n_string}) 
    
    #4 & 5 odd ratio and ci
    ind, aor, ci = framing_aor_ci(df_merge, var)
    result['Addjusted odds ratio'] = pd.Series(aor, index = ind)
    result['95% CI'] = pd.Series(ci, index = ind)

    
    return result

def T3_component(df_merge, var, base):
    """ this fct calculate components use in a raw, used in table 3 & 4
    Args:
    ------
    data(pd.DataFrame): Dataset containing all data
    var:  interested variables
    base: denominator for interested variable
    
    Returns:
    ---------
    table(pd.DataFrame): Dataframe with 5 components as column, group as row index

    """

    #1 weighted sum of variable by group
    df_merge['Weighted cases'] = round(df_merge[var] * df_merge['weight_sample']* df_merge['sampleweight_clean'], 0)
    weighted_byg = df_merge.groupby(['group'])['Weighted cases'].sum()
    #distinguish variables that average number 
    if base is None:
        #2 weighted sum of variable's base by group
        df_merge['base'] = np.where(-df_merge['Weighted cases'].isna(), 1, 0) 
        df_merge['Weighted base'] = round(df_merge['base'] * df_merge['weight_sample']* df_merge['sampleweight_clean'], 0)
        num_byg = df_merge.groupby(['group'])['Weighted base'].sum()

        #3 average by group
        avg = round(weighted_byg / num_byg, 2)  
        result = pd.DataFrame(avg, columns = ['Weighted cases'] )
        #covert variable into unit interval
        df_merge['num_positive'] = np.where(df_merge[var] > 0, 1, 0)
        #4 & 5 odd ratio and ci
        ind, aor, ci = framing_aor_ci(df_merge, 'num_positive')
        result['Addjusted odds ratio'] = pd.Series(aor, index = ind)

        result['95% CI'] = pd.Series(ci, index = ind)
    else:
        df_merge['Weighted base'] = round(df_merge[base] * df_merge['weight_sample']* df_merge['sampleweight_clean'], 0)
        num_byg = df_merge.groupby(['group'])['Weighted base'].sum()
   
        #3 ratio of 1 & 2
        #trans type for cauculation
        result = pd.concat([weighted_byg, num_byg], axis = 1) 
        result['Weighted%'] = round(result.iloc[:, 0] / result.iloc[:, 1] * 100, 2)
    
        #4 & 5 odd ratio and ci
        ind, aor, ci = framing_aor_ci(df_merge, var)
        result['Addjusted odds ratio'] = pd.Series(aor, index = ind)
        result['95% CI'] = pd.Series(ci, index = ind)

    
    return result

def panel(df_merge, varlist, option = None):
    """ this fuction loop through variable list assemble result from compoment functoin and create a whole panel 
    Args:
    ------
    data(pd.DataFrame): Dataset containing all data
    varlist: list of interested variables
    option: by default would sent to t3 component unless specify option as 'T2', then it'll be sent to t2 instead
    
    Returns:
    ---------
    table(pd.DataFrame): Dataframe with varlist as row, group as columns

    """
    df = []
    key = []
    if option == 'T2':
        for i in range(len(varlist)):
            df_new = T2_component(df_merge, varlist[i][0], varlist[i][1])
            df.append(df_new)
            key.append(varlist[i][0])
    else:
        for i in range(len(varlist)):
            df_new = T3_component(df_merge, varlist[i][0], varlist[i][1])
            df.append(df_new)
            key.append(varlist[i][0])
            
    panel = pd.concat(df, keys = key, axis = 1).T
    return panel

def Table(df, query, key, varlist, option = None):
    """ looping through panel with order all, female, male
 
    Args:
    ------
    data(pd.DataFrame): Dataset containing all data
    query:  query for panel's data selection
    key: name of the panels
    varlist: list of interested variables

    option: by default would sent to t3 component unless specify option as 'T2', then it'll be sent to t2 instead
    
    Returns:
    ---------
    table(pd.DataFrame): Dataframe with varlist as row, group as columns and with extra layer of panel """
    df_panel = df
    panellist = []
    for i in range(len(query)):
        #rule out all
        if query[i] != '':
            df_panel = df.query(query[i])
        panel_new = panel(df_panel, varlist, option)
        panellist.append(panel_new)
    #combine results
    table = pd.concat(panellist, keys=key)
    return table

### generating / formatting variables columns needed in table 2
def month_diff(start_date, end_date):
    #cauculate month diff
    num_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    return num_months
df_merge['month_diff'] = df_merge.apply(lambda x: month_diff(x.Q_a2_7_realdate, x.p2_a2_7_date), axis=1)

#hiv
df_merge['HIV'] = np.where(df_merge['p2_c2_233_hiv_result'] == 1, 1, 0)

### generating / formatting variables columns needed in table 3
#ans in stirngs 3 category
df_merge['Ever received free condoms'] = np.where(df_merge['p2_b8_200_condomsfree_ever'] == '1 Yes', 1, 0)
df_merge['everfreecondoms_base'] = np.where(-df_merge['p2_b8_200_condomsfree_ever'].isna(), 1, 0)

df_merge['Ever used the free condems'] = np.where((df_merge['p2_b8_202_condfree_use'].str.contains('1') | df_merge['p2_b8_202_condfree_use'].str.contains('2')), 1, 0)

df_merge['Ever sold/gave condoms'] = np.where((df_merge['p2_b8_202_condfree_use'].str.contains('3') | df_merge['p2_b8_202_condfree_use'].str.contains('4')| df_merge['p2_b8_202_condfree_use'].str.contains('5')| df_merge['p2_b8_202_condfree_use'].str.contains('6')), 1, 0)

#ans in stirngs 2 category
df_merge['Ever had VCT'] = np.where(df_merge['p2_b9_204_evervct'] == '1. Yes', 1, 0)
df_merge['evervct_base'] = np.where(-df_merge['p2_b9_204_evervct'].isna(), 1, 0)

df_merge['VCT more than once'] = np.where(df_merge['p2_b9_205_timesvct'] > 1, 1, 0)

df_merge['VCT more than twice'] = np.where(df_merge['p2_b9_205_timesvct'] > 2, 1, 0)

#ans in stirngs 4 category
df_merge['Currently married p2'] = np.where(df_merge['p2_b5_115_married'] == '1 Currently married', 1, 0)
df_merge['currentmarried_base'] = np.where(-df_merge['p2_b5_115_married'].isna(), 1, 0)

df_merge['Sex in last 6 months'] = np.where(df_merge['p2_b5_118_sexpartners_6mos'] > 0, 1, 0)
df_merge['sexpartners6mon_base'] = np.where(-df_merge['p2_b5_118_sexpartners_6mos'].isna(), 1, 0)

df_merge['Ever used condoms'] = np.where(df_merge['p2_b8_182_everusedcondom'] == '1. Yes', 1, 0)
df_merge['everusedcondom_base'] = np.where(-df_merge['p2_b8_182_everusedcondom'].isna(), 1, 0)

df_merge['Used condoms last time'] = np.where(df_merge['p2_b8_186_condom_lasttime'] == '1. Yes', 1, 0)
df_merge['lasttimecondom_base'] = np.where(-df_merge['p2_b8_186_condom_lasttime'].isna(), 1, 0)

poly = (df_merge['p2_b5_119_sexpartners_life'] > 1)
poly_nocondom =  ((df_merge['p2_b5_141_p1_condom'] == '5 Never') | (df_merge['p2_b5_141_p2_condom'] == '5 Never') | (df_merge['p2_b5_141_p3_condom'] == '5 Never'))
df_merge['Unprotected sex non-monogamous'] = np.where(( poly_nocondom & poly), 1, 0)
df_merge['polynocondom_base'] =  np.where(- df_merge['p2_b5_119_sexpartners_life'].isna() , 1, 0)

df_merge['Self reported STI'] = np.where(df_merge['p2_b10_214_sti'] == '1 Yes', 1, 0)
df_merge['sti_base'] = np.where(-df_merge['p2_b10_214_sti'].isna(), 1, 0)

df_merge['Ever or partner ever pregnant p2'] = np.where(df_merge['p2_b7_148_pregnancies_number'] > 0, 1, 0)
df_merge['pregnant_base'] = np.where(-df_merge['p2_b7_148_pregnancies_number'].isna(), 1, 0)

df_merge['Named 3 prevention p2'] = np.where(df_merge['p2_b4_72_protecthiv'].str.len() > 4, 1, 0)
df_merge['named3prev_base'] = np.where(-df_merge['p2_b4_72_protecthiv'].isna(), 1, 0)

# hiv knowledge
# choose highest replied question as base
hivq1 = df_merge.p2_b4_74_hivinwomb.str[0] == '1'
hivq2 = df_merge.p2_b4_75_hivbreastfeed.str[0] == '1'
hivq3 = df_merge.p2_b4_76_hivmosquitoes.str[0] == '2'

df_merge['correct'] = np.where(hivq1, 1, 0)
df_merge['correct'] = np.where(hivq2, df_merge['correct'] + 1, df_merge['correct'])
df_merge['correct'] = np.where(hivq3, df_merge['correct'] + 1, df_merge['correct'])

df_merge['Answered 3 questions p2'] = np.where(df_merge['correct'] > 2 , 1, 0)
df_merge['ans3q_base'] = np.where(-df_merge['p2_b4_73_stiandhiv'].isna(), 1, 0)


#question relative with attitude toward plhiv
# choose highest replied question as base
object1 = ((df_merge.p2_b4_111_hivpunishment.str[0] == '5') | (df_merge.p2_b4_111_hivpunishment.str[0] == '4'))
object2 = ((df_merge.p2_b4_112_hivprostitutes.str[0] == '5') | (df_merge.p2_b4_112_hivprostitutes.str[0] == '4'))
object3 = ((df_merge.p2_b4_113_hivpromiscuousmen.str[0] == '5') |(df_merge.p2_b4_113_hivpromiscuousmen.str[0] == '4'))
agree = ((df_merge.p2_b4_114_hivtreatedsame.str[0] == '1' )| (df_merge.p2_b4_114_hivtreatedsame.str[0] == '2'))
df_merge['Showed positive attitude p2'] = np.where(object1 & object2 & object3 & agree, 1, 0)
df_merge['posplhiv_base'] = np.where(-df_merge['p2_b4_112_hivprostitutes'].isna(), 1, 0)



df_t3 = df_merge.rename(columns={
                                       "p2_b5_118_sexpartners_6mos" : "Partner number last 6 months",
                                       "p2_b5_119_sexpartners_life" : "Partner number lifetime",
                                       "p2_b7_148_pregnancies_number" : "Child number" 
                                     })

### generating / formatting variables columns needed in table 4
df_t3['HSV-2 female'] = np.where((df_filter['hsv2_positive'] == 1) & (df_filter['sex'] == '2 Female') , 1, 0)
df_t3['hsv2_accept_f'] = np.where((df_filter['hsv2_accept'] == 1) & (df_filter['sex'] == '2 Female') , 1, 0)
df_t3['HSV-2 male'] = np.where((df_filter['hsv2_positive'] == 1) & (df_filter['sex'] == '1 Male') , 1, 0)
df_t3['hsv2_accept_m'] = np.where((df_filter['hsv2_accept'] == 1) & (df_filter['sex'] == '1 Male') , 1, 0)

