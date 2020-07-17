--- 
Project for the course in Microeconometrics | Summer 2020, M.Sc. Economics, Bonn University | [Ying-Xuan Wu](https://github.com/amanda8412383)

# Replication of Duflo E, Dupas P, Ginn T, Barasa GM, Baraza M, Pouliquen V, et al. (2019) <a class="tocSkip">   
---

This notebook contains my replication of the results from the following paper:

> Duflo E, Dupas P, Ginn T, Barasa GM, Baraza M, Pouliquen V, et al. (2019) HIV prevention among youth: A randomized controlled trial of voluntary counseling and testing for HIV and male condom distribution in rural Kenya

##### Downloading and viewing this notebook:

* The best way to view this notebook is by downloading it and the repository it is located in from [GitHub](https://github.com/HumanCapitalAnalysis/microeconometrics-course-project-amanda8412383). 

* Other viewing options like _MyBinder_ or _NBViewer_ 

* [travis-web]()


* The original paper, as well as the data provided by the authors can be accessed [here](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/CVOPZL).

##### Information about replication and individual contributions:

* Due to the unavailability of original code and the massiveness of the dataset, the estimations all differ from the original paper in various degrees.

* One of the most important outcome variable isn't found, the attempts on searching it is documented in section 7

* For the replication, I try to remain true to the original structure of the paper, all the panels and rows are lined as they appear in Duflo et al. (2019) and named identically.

* some of the columns feature in my replication appear as second-row indexes compared to the original tables, and the incidence rate has become independent to suit my workflow in Python.

##### about the paper

Duflo et al. (2019) examine the effects of Voluntary Counseling and Testing for HIV (VCT) and increasing access to male condoms compared to standard available HIV prevention services, using biological and behavioral outcomes, among youth in Western Kenya. VCT, serving as the entry to HIV treatment and care, is a test of accessing one’s HIV serostatus, in addition to receiving individualized risk-reduction counseling. VCT is supposed to help individuals reduce risky sexual behaviors and prevent themselves and their partners from HIV and other sexually transmitted infections such as Herpes Simplex Type 2 (HSV-2). Even though some of the previous studies show the reduction of risky sexual behavior in testing-positive individuals, other studies bring about the concern of disinhibition among those testing negative (Sherr et al. 2007). 



##### notebook structure 

In this notebook, I attempt to replicate the results presented in the paper by Duflo et al. (2019) but only acquire similar result and failed to find one of the most important outcome variable.In section 2, the methodology adopted by Duflo et al. (2019) is presented, regarding how sampling, treatment, randomizing and tracking are conducted. In Section 3, possible identification is brought out from 3 different aspects, containing selection bias, measure error from self report, and externality. Section 4 briefly discusses the methodology used by the authors. Section 5 shows my replication of the results in the paper and discussion thereof.  Section 6 offers  discussion on insignificant results. Section 7 reveals my failing attemps on finding HSV-2 testing result at baseline.

##### reference

* **Canning D. (2006)** _The economics of HIV/AIDS in low-income countries: the case for prevention. J Econ Perspect._ 20(3):121-142. doi:10.1257/jep.20.3.121

* **Coates TJ, Kulich M, Celentano DD, Zelaya CE, Chariyalertsak S, Chingono A, et al. (2014)** _Effect of community-based voluntary counselling and testing on HIV incidence and social and behavioural outcomes (NIMH Project Accept; HPTN 043): a cluster-randomised trial._ Lancet Global Health. 2(5): E267–77. https://doi.org/10.1016/S2214-109X(14)70032-4 PMID: 25103167

* **de Grange, L., González, F., Vargas, I. et al. (2015)** _A Logit Model With Endogenous Explanatory Variables and Network Externalities._ Netw Spat Econ 15, 89–116. https://doi.org/10.1007/s11067-014-9271-5

* **Duflo E, Dupas P, Ginn T, Barasa GM, Baraza M, Pouliquen V, et al. (2019)** _HIV prevention among youth: A randomized controlled trial of voluntary counseling and testing for HIV and male condom distribution in rural Kenya._ PLoS ONE 14(7): e0219535. https://doi.org/10.1371/journal.pone.0219535

* **Duflo E, Dupas P, Kremer M. (2015)** _Education, HIV, and Early Fertility: Experimental Evidence from Kenya. American Economic Review._ 105(9):2257–97.

* **Fonner VA, Denison J, Kennedy CE, O’Reilly K, Sweat M. (2012)** _Voluntary counseling and testing (VCT) for changing HIV-related risk behavior in developing countries._ The Cochrane Library. https://doi.org/10.1002/14651858.CD010274

* **Greene (2006)** _Econometric Analysis_

* **Hansen B. (2020)** _Econometrics_

* **Miguel, Edward, and Michael Kremer. (2004)** _Worms: Identifying Impacts on Education and Health in the Presence of Treatment Externalities._ Econometrica 72 (1): 159-217.

* **Sherr L, Lopman B, Kakowa M, Dube S, Chawira G, Nyamukapa C, et al. (2007)** _Voluntary counselling and testing: uptake, impact on sexual behaviour, and HIV incidence in a rural Zimbabwean cohort. AIDS._ 21(7):851–86 https://doi.org/10.1097/QAD.0b013e32805e8711 PMID: 17415040


