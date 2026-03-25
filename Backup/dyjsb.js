/*
目标: 抖音极速版App 抓包https://api5-normal-lf.toutiaoapi.com域名url里的device_id iid 请求头cookie里的sessionid用＆连接 不分顺序

格式：export dyjsb="sessionid=xxxx&device_id=xxxxx&iid=xxxx"  
多账号换行隔开
教程地址：https:wjkjs.top
cron: 32 0/30 * * ?
*/

const $ = new Env("抖音极速版");
let envSplitor = ['\n']  //多账号隔开方式，默认换行可自定义

///////////////////////////////维护参数自行更换//////////////////////////////////
let defaultUA = ''                    //默认UA

var version_='jsjiami.com.v7';function _0x2c25(){const _0x1a2e0f=(function(){return[...[version_,'kMjNsjtFiAfaSOGmwi.ecAotmEO.rLvnO7nnAUMG==','nmkZW4HOa8o7Bcq','bmoYWO7dQmk+','AUw+UEwVPUEULZyQ','oSkPW7ytW7DDW7C','WPdcU2JdLurG','gCkiW6tcV8kP','Dhm2W5CCsftdM2q3','iKD8WQpdQmogW5aojrNdPSohlaDMfhSIWRRdSmkjWQhdLCkCWOdcPCo3iSoBWOCpW6TmbW7dLqTYW4SrC0Dpq8kwW74PC8kZxSkvWOmOWO7cJdNcKCkQzJldUv/cVSkSlGFcTxhcG8oOWPP5CJesWQVdMGeNWRu1mLvTWQfNaGddICoQaq','W5Xcyhu','WPxdGshdLmkBWPpdQ1ZdLq','W5uuWRWV','WOWKW7BcHLa','WOD3WQnzmH3dKW','kwf8W4K','W67dIGq','W7K7W4epWPxdOCkW','n8kyF0FdVa','W4NdSYiUoSkwW4K/W7HWWPRdKhK','WOdcGCk8WRFcJW','eow6GUwrVUI/JowiUYCR','yMq3W7SBsa','nEAEKUAiIowjSmomWQCF6k+h6zIF6k2G6iwj5P+n6kYJ5PIX','W4jkr3ZcKa','iYpdNCkoAW','WOCwW4iVDbtdS8oEj8kLoG','WQK9mSkKCq','6lEC5y6YW4e','zaP5W4RdSSoEWRRcIta','WPiXW67cN0FdQZSOWQqVWQVdS8oaWQVcJSklW5ugo8oTk8k2W710lCkaW47cJJZdMZxdUIWGh3D9WOddKSkzAmoDWOxcQhPTW6RcKmkGwJtcNCkRjGdcMmkQWPegW4PBhSkaW5tdV8o2xG','W4T1WQ/dNaxdPeDjWOCkWQ/cGa','lSkCW7WDW7q','h+s7G+AuSEMfTUw7S+AuPoweNZG','W4/dGqbEWO8','WPNcOMRdT2i','W6zUnq','W5SUWQvgWPeoW7nRbCknWQ7dIG','ESkVrCk5','W5msW4uYWRC','uCoOW7ldV8kT','emolWPXAWOurW5JcKhq','W6SGgKC','lv1nwSoZjmoYW5JdRgT7t8kzn2xcUmoyr8kgWPjCqGhdSWy6W5/cIgxdH8kVfepdHgxcLtRdG0WDDxe9W6nlW6ZdRmkgi8kK','aCkzW6RcGSk9','mMJcPSogWP8','WOlcL8oCWO4','W6uGgx9ZaSkUWQ4mWPJdS8kB','WRixemkcza','W4SBWRe+da','WR3cHSozWOJcSG','ALfls8kGySoW','WP7cK8oaWRtcNSor','WQpdPSksaCkRBmonpmovkmk2WOq5W4Xjmtf4W4usWOCfWQ0qaKldRNdcUCoDW5K','gmo4lYvE','BCkezmk/BG','WPdcP2tdRubHW7XB','WPJdUSkljmk0','WQRdSwFdTCk0u8oSpHbIW7y','W6msW4H8W5C','W47dMIP+WRm','ChKVW50w','W7KGduO','WRldT8kqdmkV','W6BdHG7dHmoRta','aSouW53cN2K','fvqHW7JdMSo4WOhdGHxdVq3dUgLg','AxbPwmkH','x+w7LEwtSUI9IEwjHSkaWO8','WR8eW7vUW5KCWP9nW4y2W6q','jNH7W4bp','WQVcVmkAqq','yaCpuCk0W4amxNRcSfNdHcSRW6yNECo/dq00amk2nwfdWO0kWPRcS2SqwWJcHKn0emkZWPZdRmolWRuvr8kzWRZdOmkEr8k4qSkoWP1UnmoPsmo3WR/dOb3dTCotW5iM','6lsz5y2plq','D0OCCCkPW48DwMVcOb3cHW','ymoRd1rB','WPRcSwldM1LVW7PxWPC+BCoHW5fOuSkwW5rK','jbtdOmkJsSop','jaX3WOqN','W610WQ0o','WRhdTCknh8kNumonjCotmSk2W58','fSoMWR3dQmkU','6lEe5y+zWO4','WPncWOvNgXldLCoRf8otgmodW48ddWxcOq7cG8ohbfpdGxNcLCoqWPadW5NcSdSkWRqAoCkUDZ82B8oeWRtdUWbqmCosrXrW','lmkRW6BcMq','jSkfr1NdNG','W5BdUxRdSmkQ','WPOPW784W6vgW7yKsSo5W6eEkSktW68DtmkDFIZcQCkWWRpcKmoUWO14W4NdTaNcM8oQWOJcRmkvcCo/o3tcUgZdM8obWPHWhSoKyCkGeCoobtu9W7BdLcNcJCoExqRdUM/cN1yqr8o2ACoVuqNdMCoMqGFdJSoUjeBcUCoaeZ0sdx0dW7RdSb3cSv7dRsZdJd8Lh0pcPqPxW6NdLMDMW6xdNLZcRg/dHSoZrSoHeuNcOKqJWRmmW51DW4CXW7lcMCkJWPakc8kFWRb8r8kZpsRdS8o1zSoOkHzvW6v8hwL+uSovWOJcPCkFrGhdTh98qCogaNlcLCkeW5jIWRJdTCkSW5f/W4ZdQttcGa9eW67dRZm','DK7cU8kos8oyWQGjWQW','y0HqtSk9lmoUW4xcTd1ZcSoebMtcQ8oyq8oxW5TqgHtdVeyeW57cHhZdLmkNauNdMZNcKcddJNGkD30SW7eyWQJcP8oCAmk7W4iOWQesWPFcOc1JgCoMWQfRWQ4WWO/cG8ohE8kUemomtxXwsdGxrCkYWOpcQw5hWONcPgtdKwjHW5VcHSo9t8odW4tcQeG7WRO','W73cT2HpWOe','W5tdOrryWQa','W7bOWRFdGHNdVdKQW6HYW6/dQ8oaW6JdJmoz6lAE5y6q5Qkx5RAlAmk2WRW/lSomWO7dHNZcGdBcTg5Ghq','WOdcG8kuWOFcUG','WPzQW5e9W48','wuyq','WO4qjMtcLaPhkfC','ECkJwCk/whGXbM3cVG0q','E3Spr8o/hmkjW74lmMtcQW','6lwJ5y6oW5q','WPVcQhxdKW','lmkqw0tdTwK6','W7WsW6jhW4qwWOPH','WO3cRhhdNKXTW6S','WQRcR8kCFXhdRG','lbddQW','iw9VW6LKrConBXP1kmkC','W5TiqNxcMIH5','W77dShhdRmkXrSoS','o8obW6ier8krWRnslNpcOSo7WPq','WOT7WOdcIN4','W6H2WQWEAuW','jmksEwhdGq','WPxdGshdLmkBWPpdQ1ZdLwK','BCkwWR9vimobW6ro','WR3cUmkDtXpdT8oN','W7ajW7q','WRmxo8kiDa','kCkNW73cJCkxWOy','W7G1W4SK','iSkGW4b8hq','DhuQW5yqEfVdN29/w3a','mmkSW5vcgCoM','iCkdW44uW4e','W65+WRC','WQL8W5iTW6e','W47dGqvd','W6CUe1S','WOFdLcldI8kBWP/dPehdMdTzW6tdRftcMSkkowRdMCojW5dcHCobemkkW63cNcpcS8o4nW','eColWPXgWOaiW5m','y8ohW5FdGCkiW47cNG','rUECRUw4HowrUSo9WOVOJ6tLVQi','6lsI5y+rtG','wmoDaHtdPSkbwG','ECkPuCkJyK4+','krBdQmkxsSoFWQ8mWQldRmoYWQy','cCoAmJ96lmojvSo+W7tdQN3cHSk8WOVdQmk8mSkkW5XMW74pW5RdOcn8qCoBwCkOW50PprapW50MfSkzBCkOz8oeCCokoqdcOd3cLZpcQb01cI3cTauNW7DsWQb4vuvYwM/cLSodFSouESkabKNdP8oRx8okW7bQWOtdICkEW7NdNSo+WPdcQmkOW5NdJa','FSoanMLg','lSkwyLddT3rV','mLO7W60','hUs9UUMJUuK','W47dOuJdU8kV','kragtmkRz8kEWOpcSw8Ghq','r3aRy8oA','y8ohW5FdGCkiW44','t+wTIUETTow5NowrN8oyW40','vCo/BSotW6a','WOzbWRVcVgGYsSo0','W6TPmSk/WQJdSrBcOCkLW5ldKG','6yEv5BINnEEFJow6QUwsVUMHP+IUNEwpS+IoIow8Kmkn','W71hCxJcVG','FuWvuCkRW4CQ','W5hdHq1tWO7dMW0','z8kaWQfqyW','6lsy5y+upW','WO0ve8kowa','WPtdGspdUmkBWPG','p20CW4tdLG','WR8hdSkmyG','ySkIWRzl','z8oyW4RdQ8ksW5pdN8o7','zSk4ySkxvW','W4hcGwHjWOi','WPNdVwmnEmkdWOGW','W4buWOi6ua','iCksuW','WRZcUmkDuXBdRSoSW6Tgya','FSkYWQTeyCkk'],...(function(){return[...['W7L0WRaF','WPqZe8k/vG','nComWOddL8kh','yK9QuCkQCW','WPvpWRZcRq','WPblWQBcTLSHtG','WQZcVmkaCHRdOmoM','AmosBSobW4PjgIxdMNS2WOBcUZ8XWRKBzfy1W4VdVhpdTSoVk1rKcZT0rGHDumoWWR8BW4/dPsZcJw5uW59jW6vxa1HaW7xcICktW6tcJmo5W6TrDLRcQtlcNCkVymolkCkHcmoAWOZcJ8kedhZdGfKapMjWW5jWDSkRcaORWQzuW4pdOCoPlSkcWPupWQH0ExbCvfSYW4LDn8oyWOlcMMpcT2xdVt3dI0aSlsFcIq','F1yTbCkD','FmkHwSkKwq','jmolW5hdKmoBWOJcNmk6WRfnW7iEWQ7cK8oPW6JdNZPaWO7dTf8/WQP1lJJdLmkZW7VcVCkyWR7cV8o3WPdcQ8k4WOpcVmk/nSoasvSeBhrOk8kTs8o/WQVcVbFdSZbqW58ZcIpdTSopW5VdJd3dUXDKpSoJWQNcMCk7W5BcISkcaGbiW4GDpSkdWOJdJtDKW5G','WRfmWOlcRKy','paHKWOeVW77cNG','m0K9W5pdI8o/WOxcNa','lCk4W6dcP8knWPVdIJa','oLqOW43dKCoYWRVcGc3dSqxdPG','W410WOK4CW','zMXTWOxcPW','WPpdV3q8BSkfWOa','5B6p6ygb5OE7776O6yAK5BIM5RQM6lEc5lQg772u','W6eTWPTfWRO','w8owhgDIBJDSW5K+W4Sg','y+wpN+AUV+s5VUILKowLIoI1H+w/QowsNE++Ro++KG','WR82W5dcQvW','WRGRW7zynG3dIxO+nmoPbG','b2XBW4XC','WQ7dUCkf','WOr5W7KgW6jeW5K8','jNdcVSouWPa','W4ChWQCeamo4WQ0z','zSkVuq','WOL/W78PW6uxWOzGwCkXW61oyCkyW6uxvSkbDJVcQCoXWR7cOmoIW4y7WONcUKBcNmo2WPlcRa','ESoYWQhdJmobW4FcJcTGWP0yc2K','e8oJWPBdOa','CSolW4RdLCkl','WPBcP2xdL1u','pSkeW4pcGCkq','W7fVpSkNWQJdPY4','BN8H','W78OkvD0','WOJcN8ov','WQRcPCknsqVdOmo2W6Tnm8o7W5pdJX7dQ2tcQ8kfgCoSjSoBqmk+W7KE','zSkjWRrEhColW70','yxfRASkH','mqnZ','W7JdPdLbWQi','u8oZvmoqW5q','W7JdPdxdP8o+','y+IoLowoSUw4JowsM+woOoAuNEAiU+wlPmkmWRpPOR7OR5BLJkpOJz7LV4Gb','WRj0WPNcLvO','vUw5G+wrRUI/G+wjRIZdOEInNEw9GG','jSkRW7/cNq','W5rmC1xcMcvtdKjDFmoo','WO9QW6y8','W747W5S8','E8kCWQjFe8osW6a','WQVdUmkgcmk6','ymkxWRvvbW','oajI','W7zLn8kJWQK','W6SfW6n3W5WjWP8','W6fQxvZcMW','W6BdJaFdOSoXqmolWOzFo8o0WOa','WPfKW7GT','jmo0WRRdUCkF','pqnHWOaY','xuWkb8k0dbK','pMv7W5TJtSoTAqO','W5mGWRzM','vCkUW4ddOmkUWOpdHCogWROmAbe','nmkZWQbvFmkbWOJcOf7cH8kS','W41WWQ3dNWtdPwvoWPa9WPxcSW','WQ8Uf1OGvmotW7nbW5FdTmksrCkmtCo+b2TiAr3cHeS8WPRcQd7dUSknwc3cQW/cRX3dR8k6rmkunwjFyNbOaCkJduBcLtu+hdG9W4TaxCkjWR/dNqLNremRW45tECoyW5G4W5LJxmkaW5NdJCo6W4dcHgtcTW','wmk7WQD3lW','6lwR5y+3uW','WPjpWQFcUfO','nCkGW45w','W5LmWPi','iwJcUSo1WPDZhG','eowmGEAVR+s4VoIKMUwKT+I0OEw9TowtIU++O+++VG','6lA/5y6xW4S','CCopW4VdH8kpW5xdGCoHW6W','WQ/dTLOhsq','uKWdmSk/bIned8oeW7vd','rvSXASoh','WO0OW7ZcVhy','vveOW4G2','E11wx8kJ','W47dUZdcIH47W5XDWQ0xqCol','o8kVW6hcI8kqWP3dLcPYW4q','i8kKW4Lyg8oKEq','i23cI8ooWPy','6lsK5y2DW6m','zSkLwmkQsu8','WOtcJmkJsbS','D8ohC8of','nrJdVCkLqq','qmoyeLi','zCouAmoUW40ArxK','W7flELBcSa','W5PbWP9YjWG','aSobkdTSEmks','W4FKVlRKVO/NM5NLJllML7dMLltMLR0','W5j3WROLWQzrWP0Zhq','W5rhWQP+ia','6i+/5B2BWR8','z1nd','W7/LJONMRi7KUzBOP7xLPRVOT7FLVQNLKiZVV4tVVRK','FCk1F8k+zW','5l+y5PIm5zgs55oi5zUTyE+8GG','W43dPs3dTmoX','5lQM6lAZ5y+1','WOpdLs0qW58jqCkwW7b1ta','WRZNRBxLIRTJWRy','uSkbFCkOrq','WOZcRhldGurHW6bxWPW','tCoMW73dL8kp','rmojf094','ySk2WRDcEa','W5LmWPjwkHJdUSoPbSkhgSov','bdVdHSkezG','WOBcUCoaWPZcVa','e8oGWQ5CWR4','W4X+WRenyW','WPnVWOtcLhm','krZdOCkXumot','WP3cPMxdIW','ASk9WR9/oW','W6yJefbz','W4q1WRa1WPuzW5jQ','W4TsWO4ZuW','WPVcOgu','W5uUWQz+','jLq8W7G','6lAF5y2xnW','F8kPyN/dRxXS','w8ozaIe','iHZdU8kYrCopWOa','uCoMWOFdT8kJWR/dKSoWWQDkBW','ACkVwmk5weKK','BmoJW4RdMmkx','5l6m5PUz5zo355c35zUSWPxVVyS','W7y1W4GCWP7dPmkAWPRdUu0lW5W','W6xdU2hdRmkWvCowbrHYWQO','tmoDgcq','W7pdJrrqWQK','C8o2fMnb','W5LWWPbzdq','WPyQW73cRLRcTvPOWRe2WQtcVW','W5xdJWS','BmodDmowW40B','kCkCqfa','DwacxCkc','FmoqeGxdVq','DKeNWOqNW6pcMcldP0DIEG','WQZdHWxdLCo2r8oGWRzcnSkV','W4OFchj7','BNDfCCkO','W5iKWObTWRy','ASkQWRXDmG','oCoJWRpdQCke','eSo6WOhdQmk+WR3dG8ogWQfadvldMSkiWOXaAtK','eCoFWR5RWRG','W5ZdQW14WO0','W4CGWRb0WPO','6lsH5y+HhG','W7lcSh1YWRG','WQZcSSkavbRdR8o2WQ9wjmouW5C'],...(function(){return['W6RdIYzoWOC','W5brWODimbxdHmo1','W5LVWO4bCq','yCkYWRzqFmknWOpcLLpdNG','a8k6W7WmW5m','r8oycuDH','W44qWRS8amo5','W6z1WQy0ALFdQfe','dmo/WOPHWOe','b8oJWPddOmkN','F0apuCkUW4C','WQTMW6fhjvNdVMSDdCoTiCo/WQP1WPKQz8oSWP/cJmk5WRPevY4UlYdcRSooW49kh8oamCouW6xcVuNcLmkEBSkXgW','W5NcLg5yWPXBkCoHW4roy8kOW77dSbqwnCk4paZcMmokpW1uCGqStHOZCSk/W7LNWQZdIHdcHZTSCfKVW7buW7pdOejVCCokWRLQFmo2WP08W59sW7CoW5rxWR7cPCoDW6RdPc1yW70oWPddTcrOnCo8pNldGuuCW5pcMeWVWOZcIWZdJwnWW73dUmkVmSoM','jmkLW7xcUCkxWPBdTcXIWPaika','WQFNNy7LU6xLKQuoW7e','WQpcSSkj','mbrVWPyO','lmkLW6e','uM9VWPdcTG','WPhcQgZdLW','W4RdGWnfWO7dTH/cOYZdHGGH','A0qjuCkQ','W7K1W4ePWPxdRSkGW5JdUv0DW4a','rUECRUw4HowrUSo9WOS','h8o2WPBdSCk5W6BcMmkaWQ9EoWBcK8k5WOPCyJFdVd4oW7n3qCoXeqDBW7TLW7xcJCkQdCkCWPPbgvJcJmkEtComWQyXwtn3W7ddOhxdJwdcQCo7W6xcTMlcQ8oMWQBcJ3OgWRTmW5OVa8oitJSyhCoTmmo1','W6ldTg/dPG','WQ4Gi8kovCooCa','W6KbW6j5W50','lSkJW77cJmkCWOa','W4zaWPPLispdLCoRhCkBeSoy','WO3cM8oEWP7cMCobzq','WQuKlmk4vCoDzW','WQJdU8kBlmky','W5DnCuVcMY5Vba','W7JdQmozee/cTCoZW4T3p8oZW4C','D0DVWOZcVW','WOLjW6euW7q','WPfQW7K4W7S','WRT4W6OCW6e','WQpdUSko','ECo9WRDmWQGtWQy2p8kiW7RdNCk1','6lsS5yY3Bq','W7PVWRfzBuVdTvO','imolWR5+WRG','t1tcOSo7cCkwW4XoW7VcQmk5W7lcQXJdJSk95AwD5AwI6lw26ysu5BUvWQmOjgpdKItdUsfwWQdcVCoTW6eTAG','qComW5tdOmkP','x04lbSk/fG','WPVcL8oyWP8','FNOmy8oP','WPiGW7VcI1hcO2C','y8oIDmo+W70','W7upW7DzW54BWRr9W5S7WR/cHW','CSoFW4VdNa','W44AWRi','W6ZNRP7LIkRLUzFLKQvBjG','msv3W5qxBgddU2e','lvpcNCoIWPy','dSkjtrq1oefkW6W0W6SPCG','W69GtedcNG','d8kIW6BcLCks','WP7dOhuR','t+ADK+AlSEwlPMFdSmob6k6u6zUt6k2+6iAo5P+Z6k2Y5PI7','eZpdUmkWuq','CmopW4VdM8kkW4ZdIG','WRVcVhBdO2i','jmkLW7u','jXRdPmkhyq','W5iAWQyV','pCoAW4xcSq','W5iaWQyZ','ugbHWOJcTG','W53dMdPXWRS','W6rPymkyvConxh/cISoBWQ/cRa','W6tdGG3dHG','EKeKwCkJ','6lsT5y+lFW','6lAK5y+WcG','ueijfG','WOKXW6JdNv7cONTP','5B236ykE5OA/776+5Aw75yQ/5RIs6lwo5lM+','6lsM5y2rqq','WPH3WP3cQga','WORdIZu','nt9NWQW+','WP09W5lcL1K','WPpcRg/dLvLM','aSodWObCWOik','tKO4xmk+','kSkJW6ef','eSoEkIz9','WQiKnSkl','mCouW4ZcRq','mr93WROKW6m','uKWd','p2v5W7DJrq','BSohD8ou','zSoje0vj','W4btWQKeqa','WOVdONCbtG','jcnCxSo+g8koW7Sf','zCkWu8kJx0GO','6lwU5yY7W54','w1ewlmk/dq','oWvX4OcK4Oot4Ok/4Ogh44c/','yvrNWPJcOCkDWPnp','teyvlmk4bG','wEETMowiPEw6UowsN8ooW4pOJOVLVOS','W5K1W4ePWPxdRSkGW5JdGuedW4jZWQy','W5xdJWT2WOxdJtdcOtFdMGaS','iCoEW5VcU2/cLa4','x+wST+ESIEw7I+wsRmkaWO8','W68hh29W','n38UW47dPG','f8o+aX9W','W7y1W4G','WOHIW68','W5yfWQn/WPq','W4/dTfRdS8k6','WPKUW4ZcJLJcUha','Cx0eCSo0cG','W5ZdKH5OWP/dGa7cVq','rmoAffrPvrHUW4iIW4ml','W5qsWPi5mW','r8oPdxbb','WORdIZxdPSkCWPJdI1RdHt1rWRi','W7SpW7rH','5yEZ5OM55yMH','mmoAW5ZcT2S','BCkZWR14lW','jCklW6RcL8kY','W5ziWQn2kbxdKa','tKiweSk8','nCocW4RcOKO','tuO4yCke','W4zgWOzKlrpdMSoVfSot','WOKTW73cHNe','zCkwWRzXeCoaW4Tvlh7cSSoy','vCoTeXldLW','WPZcOLFdK0fNW6O','yMq3W7SbtKRdGq','WReKk8kE','BSkHqSkS','oGXOWOa','z8osW5VdNCksW5VdM8oHW6CfW4WpWRRcK8oUW6FdLda','W7VdTgVdTW','nXZdVmk5smonWOq','W6aMgG','W6zMjCkX','W6JLRR7NRytLUAJLKi5gWPtOJlhLV6u','WQ7dUCkflmkSA8oIj8oilSk+W5i','WRpcK1BcKCkMfSk9WQbQmCouWQ/dRW','W5FcLwdcL8obW4tcSwddVID2WQFdLa','WO8RW77cILlcUhPIWQe','W60IW7yNWQm','aCkNW68TW7G','W6H2WQWEAuZcQa','F8omaNFdLLveW5ff','W7TmEMdcKY9PthPrDmoqebW','pxv7W4a','fmkIW7fypa','W4myWROUgSoL','m0mSW6xdI8o3WOhcHJBdTJZdVNLXWRFcL8oxbLJdKmoWWR/cLSkbcKq','W5iZWRbyWPef','W7q7W4i4','zCk2WQXx','w8oCfuf4yG','bCoNWPpdNSkJWRG'];}())];}())];}());_0x2c25=function(){return _0x1a2e0f;};return _0x2c25();};const _0x2f0247=_0x21e9;(function(_0x4ca769,_0x2ac152,_0x19c640,_0x38491d,_0x37dd0e,_0x916a63,_0x3c5393){return _0x4ca769=_0x4ca769>>0x3,_0x916a63='hs',_0x3c5393='hs',function(_0x2d4f11,_0x13535f,_0x3ccc65,_0x408533,_0x5e5654){const _0x136dc9=_0x21e9;_0x408533='tfi',_0x916a63=_0x408533+_0x916a63,_0x5e5654='up',_0x3c5393+=_0x5e5654,_0x916a63=_0x3ccc65(_0x916a63),_0x3c5393=_0x3ccc65(_0x3c5393),_0x3ccc65=0x0;const _0x24a522=_0x2d4f11();while(!![]&&--_0x38491d+_0x13535f){try{_0x408533=parseInt(_0x136dc9(0x2e8,'^@2!'))/0x1*(parseInt(_0x136dc9(0x29f,'Rfh#'))/0x2)+parseInt(_0x136dc9(0x238,'EQin'))/0x3+-parseInt(_0x136dc9(0x2e2,'NtE]'))/0x4+parseInt(_0x136dc9(0x230,'a6z^'))/0x5*(-parseInt(_0x136dc9(0x18d,'&C$M'))/0x6)+-parseInt(_0x136dc9(0x270,']tPp'))/0x7*(parseInt(_0x136dc9(0x2f7,'5Fl$'))/0x8)+parseInt(_0x136dc9(0x2f9,'4oGZ'))/0x9+parseInt(_0x136dc9(0x288,'GNuD'))/0xa*(parseInt(_0x136dc9(0x12e,'*o81'))/0xb);}catch(_0x57edcb){_0x408533=_0x3ccc65;}finally{_0x5e5654=_0x24a522[_0x916a63]();if(_0x4ca769<=_0x38491d)_0x3ccc65?_0x37dd0e?_0x408533=_0x5e5654:_0x37dd0e=_0x5e5654:_0x3ccc65=_0x5e5654;else{if(_0x3ccc65==_0x37dd0e['replace'](/[ArkeGFOtLfMEUSNnw=]/g,'')){if(_0x408533===_0x13535f){_0x24a522['un'+_0x916a63](_0x5e5654);break;}_0x24a522[_0x3c5393](_0x5e5654);}}}}}(_0x19c640,_0x2ac152,function(_0x183f7e,_0x1aea0a,_0x48e75c,_0x491f41,_0xb03a30,_0xf63cab,_0x5065be){return _0x1aea0a='\x73\x70\x6c\x69\x74',_0x183f7e=arguments[0x0],_0x183f7e=_0x183f7e[_0x1aea0a](''),_0x48e75c=`\x72\x65\x76\x65\x72\x73\x65`,_0x183f7e=_0x183f7e[_0x48e75c]('\x76'),_0x491f41=`\x6a\x6f\x69\x6e`,(0x127dfd,_0x183f7e[_0x491f41](''));});}(0x5e8,0xcc75a,_0x2c25,0xbf),_0x2c25)&&(version_=_0x2c25);let httpResult,httpReq,httpResp,userCookie=($[_0x2f0247(0x21b,'r*F#')]()?process[_0x2f0247(0x244,'k!Q8')][_0x2f0247(0x234,'T$fS')]:$[_0x2f0247(0x2a1,'Ye1E')](_0x2f0247(0x2d0,'k!Q8')))||'',userList=[],userIdx=0x0,userCount=0x0;class UserInfo{constructor(_0x3561eb){const _0x52271d=_0x2f0247,_0x3f6f64={'bLMfo':function(_0x299e39,_0x28c78f){return _0x299e39===_0x28c78f;},'IhnBF':_0x52271d(0x298,'gGId'),'SkJyl':_0x52271d(0x1eb,'^@2!')};this[_0x52271d(0x250,'h%kc')]=++userIdx,this['name']=this[_0x52271d(0x251,'Ek^S')],this[_0x52271d(0x221,'Vn!k')]=![],this['canRead']=![];let _0x3715d5=new Date()[_0x52271d(0x1f5,'K5#g')]();try{this['param']=$[_0x52271d(0x299,'SAUS')](_0x3561eb),this[_0x52271d(0x1fa,'Rfh#')]=!![];}catch(_0x558b98){_0x3f6f64[_0x52271d(0x1b3,'r*F#')](_0x3f6f64[_0x52271d(0x27b,'ITE$')],_0x3f6f64[_0x52271d(0x2c0,'FPOW')])?_0x1be734[_0x52271d(0x2cf,'NtE]')](_0x3688f7):(this[_0x52271d(0x141,'jbuj')]=![],$[_0x52271d(0x2ac,'jbuj')](_0x52271d(0x29e,'FPOW')+this[_0x52271d(0x2f0,'*o81')]+']CK格式错误'));}}async['my'](){const _0xcbc62a=_0x2f0247,_0x3ea5c1={'VIzWc':'SBJKK','QzCjV':function(_0xd177cb,_0x1c9c0a,_0x411f7a,_0x4e113d){return _0xd177cb(_0x1c9c0a,_0x411f7a,_0x4e113d);},'RvQUf':function(_0x39c907,_0x6ededf){return _0x39c907/_0x6ededf;},'baczz':function(_0x22b4fc,_0x300cd0){return _0x22b4fc<_0x300cd0;},'Ucero':function(_0x4e3cd9,_0x3e26e5){return _0x4e3cd9===_0x3e26e5;},'jMOTo':_0xcbc62a(0x10b,']tPp'),'ESUZh':_0xcbc62a(0x2eb,'8av#'),'jUeRX':function(_0x1b065f,_0x4d20d5){return _0x1b065f!==_0x4d20d5;},'lSeNI':'wzFIX'};try{if(_0xcbc62a(0x198,'T[c]')!==_0x3ea5c1[_0xcbc62a(0x2d2,'VOMW')])_0x575be9[_0xcbc62a(0x1f7,'Ye1E')](_0xcbc62a(0x274,'T[c]')+this['name']+_0xcbc62a(0x2ce,'jbuj')+_0x533051[_0xcbc62a(0x143,'FPOW')]);else{let _0x31f945=_0xcbc62a(0x18e,'jbuj')+this[_0xcbc62a(0x23a,'T[c]')]['iid']+_0xcbc62a(0x2a2,'7)v^')+this[_0xcbc62a(0x263,'!(Ai')][_0xcbc62a(0x2d1,'^@2!')]+_0xcbc62a(0x1c3,'vi[9'),_0x43afb8='',_0x341d7f=_0xcbc62a(0x2c3,'pdRu')+this[_0xcbc62a(0x2e5,'sce2')][_0xcbc62a(0x17b,'9I$%')],_0x193ff2=_0x3ea5c1['QzCjV'](populateUrlObject,_0x31f945,_0x341d7f,_0x43afb8);await httpRequest(_0xcbc62a(0x1cf,'ihcj'),_0x193ff2);let _0x4eb0f2=httpResult;if(!_0x4eb0f2)return;if(_0x4eb0f2[_0xcbc62a(0x16d,'SAUS')]==0x0){$[_0xcbc62a(0x195,'SAUS')](_0xcbc62a(0x18c,'jbuj')+this[_0xcbc62a(0x16e,'OY((')]+_0xcbc62a(0x191,'T$fS')+_0x4eb0f2['data']['income_data'][_0xcbc62a(0x1f2,'T[c]')]+'\x20余额:'+_0x3ea5c1[_0xcbc62a(0x219,'*uum')](_0x4eb0f2[_0xcbc62a(0x1b7,'NtE]')]['income_data'][_0xcbc62a(0x166,'a6z^')],0x64)+'元');if(_0x3ea5c1['baczz'](_0x4eb0f2[_0xcbc62a(0x125,'*uum')]['income_data'][_0xcbc62a(0x1d5,'Rfh#')],0x7530)){if(_0x3ea5c1['Ucero'](_0x3ea5c1['jMOTo'],_0x3ea5c1[_0xcbc62a(0x243,'r*F#')]))this['valid']=!![],this[_0xcbc62a(0x2df,'*uum')]=!![];else{if(_0x1ddb86)_0x169967[_0xcbc62a(0x169,'*upJ')](new _0x35486d(_0x1c9ce8));}}else _0x3ea5c1['ESUZh']!==_0x3ea5c1['ESUZh']?_0x54d1b1():$[_0xcbc62a(0x1d2,'*o81')](_0xcbc62a(0x1c2,'!(Ai')+this['name']+_0xcbc62a(0x267,'Rfh#'));}else{if(_0x3ea5c1[_0xcbc62a(0x154,'K5#g')](_0xcbc62a(0x1ac,'FPOW'),_0x3ea5c1[_0xcbc62a(0x2ab,'vi[9')]))return _0x60830a[_0xcbc62a(0x1dc,'FNga')](0x1);else $['logAndNotify'](_0xcbc62a(0x130,'^@2!')+this[_0xcbc62a(0x24d,'sce2')]+']你传的参数无效');}}}catch(_0x7b80b8){}finally{return Promise[_0xcbc62a(0x138,'B$xH')](0x1);}}async[_0x2f0247(0x1f6,'Vn!k')](){const _0x1dd1df=_0x2f0247,_0x2f8f90={'rGUDa':function(_0x25232f,_0x1022cb,_0x186b07,_0x45bce9){return _0x25232f(_0x1022cb,_0x186b07,_0x45bce9);},'rqQBT':function(_0x14698e,_0x355eb3){return _0x14698e==_0x355eb3;},'jGXYI':function(_0x3a122d,_0x390646){return _0x3a122d!==_0x390646;},'GFMWn':_0x1dd1df(0x14f,'B$xH')};try{let _0x2113b5='https://api5-normal-c-lf.amemv.com/luckycat/aweme/v1/task/done/sign_in?iid='+this['param'][_0x1dd1df(0x23e,'5Fl$')]+'&device_id='+this[_0x1dd1df(0x14e,'ihcj')]['did']+_0x1dd1df(0x19b,'r*F#'),_0x15d8c5='{}',_0x217274=_0x1dd1df(0x1e1,'9I$%')+this[_0x1dd1df(0x19d,'T$fS')][_0x1dd1df(0x25b,'*upJ')],_0x32194d=_0x2f8f90[_0x1dd1df(0x247,'tiyZ')](populateUrlObject,_0x2113b5,_0x217274,_0x15d8c5);await httpRequest(_0x1dd1df(0x218,'a6z^'),_0x32194d);let _0x35e999=httpResult;if(!_0x35e999)return;if(_0x2f8f90[_0x1dd1df(0x2ba,'8av#')](_0x35e999[_0x1dd1df(0x186,'5Fl$')],0x0))$[_0x1dd1df(0x137,'FPOW')]('账号['+this[_0x1dd1df(0x118,'ihcj')]+']'+_0x35e999['data'][_0x1dd1df(0x2a3,'Vn!k')]+_0x1dd1df(0x281,'^@2!')+_0x35e999[_0x1dd1df(0x158,'Vn!k')]['amount']+'金币'),this[_0x1dd1df(0x2ee,'ihcj')]=_0x35e999[_0x1dd1df(0x1d4,']tPp')][_0x1dd1df(0x1ea,'Ppiq')],await $[_0x1dd1df(0x157,'*uum')](0xbb8),await this['detail']();else{if(_0x2f8f90['jGXYI'](_0x1dd1df(0x2c2,'a6z^'),_0x2f8f90[_0x1dd1df(0x286,'tiyZ')]))$[_0x1dd1df(0x1ba,'#1)7')]('账号['+this['name']+_0x1dd1df(0x289,'sce2')+_0x35e999[_0x1dd1df(0x226,'EQin')]);else{this[_0x1dd1df(0x259,'k!Q8')]=++_0x2caaea,this[_0x1dd1df(0x19e,'hiHY')]=this[_0x1dd1df(0x23b,']tPp')],this[_0x1dd1df(0x221,'Vn!k')]=![],this[_0x1dd1df(0x181,'OY((')]=![];let _0xcbbcbc=new _0x1f114a()['getTime']();try{this[_0x1dd1df(0x28e,'pdRu')]=_0x152fd4[_0x1dd1df(0x119,'jbuj')](_0x11bd78),this[_0x1dd1df(0x14d,'vi[9')]=!![];}catch(_0x23246e){this[_0x1dd1df(0x155,']tPp')]=![],_0x1a2458[_0x1dd1df(0x147,'9I$%')](_0x1dd1df(0x2e9,'Vn!k')+this[_0x1dd1df(0x1a1,'5[mf')]+']CK格式错误');}}}}catch(_0x1a4b4e){}finally{return Promise[_0x1dd1df(0x15c,'Ye1E')](0x1);}}async[_0x2f0247(0x2ca,'#1)7')](){const _0x48b44f=_0x2f0247,_0x442609={'pPvVM':function(_0xcfe090,_0x10e5ba){return _0xcfe090===_0x10e5ba;},'nwgoq':'TQKYZ','shgiE':'BfFra','fkkEO':function(_0x5d543f,_0x1b16d5,_0x5c08fa,_0x5ca569){return _0x5d543f(_0x1b16d5,_0x5c08fa,_0x5ca569);},'qAQMD':function(_0x67b572,_0x1e1feb,_0x264afe){return _0x67b572(_0x1e1feb,_0x264afe);},'GuQdG':'get'};try{if(_0x442609[_0x48b44f(0x146,'4oGZ')](_0x442609['nwgoq'],_0x442609[_0x48b44f(0x152,'jbuj')]))_0x59774a=_0x157735['body'];else{let _0x422d76=_0x48b44f(0x2d8,'7)v^')+this[_0x48b44f(0x23a,'T[c]')][_0x48b44f(0x1d9,'Ye1E')]+'&device_id='+this[_0x48b44f(0x2db,'%ykf')][_0x48b44f(0x29b,']tPp')]+'&app_name=douyin_lite&version_name=23.7.0&aid=2329',_0x11c1ec='',_0x131861='sessionid='+this[_0x48b44f(0x2c9,'7)v^')]['sessionid'],_0x488493=_0x442609[_0x48b44f(0x193,']tPp')](populateUrlObject,_0x422d76,_0x131861,_0x11c1ec);await _0x442609[_0x48b44f(0x294,'!(Ai')](httpRequest,_0x442609['GuQdG'],_0x488493);let _0x5679c0=httpResult;if(!_0x5679c0)return;this[_0x48b44f(0x171,'7)v^')]=_0x5679c0[_0x48b44f(0x2a0,'K5#g')]['excitation_ad_info']['req_id'],this[_0x48b44f(0x273,'T$fS')]=_0x5679c0['data']['excitation_ad_info'][_0x48b44f(0x115,'#1)7')],this[_0x48b44f(0x1e9,'5Fl$')]=_0x5679c0[_0x48b44f(0x264,'Ppiq')]['excitation_ad_info']['score_amount'],$[_0x48b44f(0x1da,'*upJ')](_0x48b44f(0x1f4,'VOMW')+this['name']+_0x48b44f(0x248,'ihcj')+this[_0x48b44f(0x2d4,'FPOW')]+'金币'),await $[_0x48b44f(0x15b,'FNga')](0x7530),await this[_0x48b44f(0x203,'!(Ai')]();}}catch(_0x5e5381){console[_0x48b44f(0x215,'Rfh#')](_0x5e5381);}finally{return Promise[_0x48b44f(0x272,'Ppiq')](0x1);}}async[_0x2f0247(0x1e2,'Ek^S')](){const _0x3e2a68=_0x2f0247,_0x590cc8={'cSmmM':function(_0x3953ca,_0x21f5bd,_0x5d5d82,_0x26fdb8){return _0x3953ca(_0x21f5bd,_0x5d5d82,_0x26fdb8);},'Eerfd':function(_0x31c4d2,_0x3ccb80,_0x5c851d){return _0x31c4d2(_0x3ccb80,_0x5c851d);},'iVSHi':_0x3e2a68(0x196,'Vn!k'),'YIIHm':function(_0x576fa8,_0x2b292d){return _0x576fa8==_0x2b292d;},'qOvKi':_0x3e2a68(0x13b,'&C$M'),'aRbIt':function(_0x23ac3e,_0x128ba4){return _0x23ac3e!==_0x128ba4;},'GNPhR':_0x3e2a68(0x22c,'SAUS'),'BIMXT':_0x3e2a68(0x122,'#1)7'),'bckQE':function(_0x4a96f1,_0x57c987){return _0x4a96f1===_0x57c987;},'uRybD':_0x3e2a68(0x290,'Ye1E'),'KQMhd':_0x3e2a68(0x202,']8[d')};try{let _0x4cfbb7=_0x3e2a68(0x21f,']8[d'),_0x119fda='{\x22task_key\x22:\x22excitation_ad_signin\x22,\x22amount\x22:\x22'+this[_0x3e2a68(0x1d1,'Vn!k')]+_0x3e2a68(0x25d,'7)v^')+this[_0x3e2a68(0x115,'#1)7')]+'\x22,\x22ad_inspire\x22:\x22{\x22score_amount\x22:\x22'+this['score_amount']+'\x22,\x22amount\x22:\x22'+this[_0x3e2a68(0x1df,'a6z^')]+_0x3e2a68(0x113,'*uum')+this[_0x3e2a68(0x1a4,'hiHY')]+'\x22}\x22,\x22ad_alias_position\x22:\x22check_in\x22,\x22timeout\x22:4000}',_0x425d3c=_0x3e2a68(0x178,'5Fl$')+this['param']['sessionid'],_0x1a67cc=_0x590cc8[_0x3e2a68(0x2b7,'Ek^S')](populateUrlObject,_0x4cfbb7,_0x425d3c,_0x119fda);await _0x590cc8[_0x3e2a68(0x293,'a6z^')](httpRequest,_0x590cc8[_0x3e2a68(0x20d,'&C$M')],_0x1a67cc);let _0x2f0ccf=httpResult;if(!_0x2f0ccf)return;if(_0x590cc8[_0x3e2a68(0x255,'ITE$')](_0x2f0ccf['err_no'],0x0)){if(_0x590cc8['qOvKi']!=='TBGqN')$[_0x3e2a68(0x2f3,'%ykf')](_0x3e2a68(0x268,'%ykf')+this[_0x3e2a68(0x10f,'B$xH')]+_0x3e2a68(0x135,'VOMW')+_0x2f0ccf[_0x3e2a68(0x1c4,'EQin')][_0x3e2a68(0x200,'T[c]')]+'金币');else return _0x26b3f3[_0x3e2a68(0x1e3,'NtE]')](0x1);}else _0x590cc8['aRbIt'](_0x590cc8['GNPhR'],_0x590cc8[_0x3e2a68(0x29a,'a6z^')])?$[_0x3e2a68(0x137,'FPOW')](_0x3e2a68(0x2e9,'Vn!k')+this[_0x3e2a68(0x114,'tiyZ')]+']签到广告:\x20'+_0x2f0ccf[_0x3e2a68(0x1d6,'%ykf')]):_0x4116bf['push'](_0x34bb99['my']());}catch(_0x2f2c78){_0x590cc8[_0x3e2a68(0x10d,'Ye1E')](_0x590cc8[_0x3e2a68(0x1e5,'*uum')],_0x590cc8[_0x3e2a68(0x184,'FWGq')])?console['log'](_0x2f2c78):_0x15df7d['logAndNotify'](_0x3e2a68(0x20a,'ihcj')+this[_0x3e2a68(0x118,'ihcj')]+']签到广告:\x20获得'+_0x26e5df[_0x3e2a68(0x158,'Vn!k')]['amount']+'金币');}finally{if(_0x590cc8[_0x3e2a68(0x11e,'k!Q8')](_0x590cc8[_0x3e2a68(0x276,'NtE]')],_0x3e2a68(0x2b4,'gGId')))return Promise[_0x3e2a68(0x15c,'Ye1E')](0x1);else _0x22df64=_0x1acd56[_0x3e2a68(0x2bc,'SAUS')](_0x29abc2[_0x3e2a68(0x29c,'SAUS')]);}}async[_0x2f0247(0x12f,'Vn!k')](){const _0x1186d8=_0x2f0247,_0x34a6bd={'uFyrK':function(_0x4adeef,_0x3281d6,_0x335aa0,_0x189818){return _0x4adeef(_0x3281d6,_0x335aa0,_0x189818);},'DoJSt':function(_0x14fcd,_0xaa8bbf,_0x44d74e){return _0x14fcd(_0xaa8bbf,_0x44d74e);},'DOmEM':function(_0x10b4e4,_0x325743){return _0x10b4e4==_0x325743;},'HwYtw':_0x1186d8(0x11a,']tPp'),'uPQRq':_0x1186d8(0x183,'o0]P'),'vPEPy':_0x1186d8(0x20e,'*uum'),'oJEoV':_0x1186d8(0x26a,'o0]P'),'CPgZW':function(_0x59f553,_0x16c43d){return _0x59f553===_0x16c43d;},'oZIEd':_0x1186d8(0x19c,'EQin'),'gDRrS':_0x1186d8(0x2b6,'SAUS')};try{let _0xfcb991=_0x1186d8(0x1c9,'r*F#')+this[_0x1186d8(0x26f,'r*F#')][_0x1186d8(0x13e,'sce2')]+_0x1186d8(0x2b3,'tiyZ')+this[_0x1186d8(0x2c5,'4oGZ')]['did']+'&aid=2329&app_name=douyin_lite&device_platform=android&dpi=411&update_version_code=14709901',_0x44a1bb='{}',_0x414788=_0x1186d8(0x151,'vi[9')+this['param']['sessionid'],_0x5843ab=_0x34a6bd['uFyrK'](populateUrlObject,_0xfcb991,_0x414788,_0x44a1bb);await _0x34a6bd[_0x1186d8(0x228,'a6z^')](httpRequest,_0x1186d8(0x10e,'5[mf'),_0x5843ab);let _0x33eafe=httpResult;if(!_0x33eafe)return;await $[_0x1186d8(0x16f,'pdRu')](0x64);if(_0x34a6bd[_0x1186d8(0x2aa,'4oGZ')](_0x33eafe[_0x1186d8(0x210,'T[c]')],_0x34a6bd[_0x1186d8(0x1ed,'sce2')]))await $[_0x1186d8(0x277,']8[d')](0xc8),await this[_0x1186d8(0x22a,'o0]P')]();else{if(_0x34a6bd['DOmEM'](_0x33eafe[_0x1186d8(0x131,'ihcj')],0x0)){const _0x2596bb=_0x34a6bd[_0x1186d8(0x1cd,'FWGq')][_0x1186d8(0x28d,'4oGZ')]('|');let _0x2422df=0x0;while(!![]){switch(_0x2596bb[_0x2422df++]){case'0':await this[_0x1186d8(0x241,'NtE]')]();continue;case'1':this['amount']=_0x33eafe[_0x1186d8(0x24e,'OY((')]['amount'];continue;case'2':await $[_0x1186d8(0x17c,'5[mf')](0x7530);continue;case'3':this[_0x1186d8(0x129,'*upJ')]=_0x33eafe[_0x1186d8(0x2a0,'K5#g')][_0x1186d8(0x2b9,'7)v^')][_0x1186d8(0x20c,'9I$%')];continue;case'4':this['ad_id']=_0x33eafe['data']['excitation_ad_info'][_0x1186d8(0x1c1,'7)v^')];continue;case'5':$[_0x1186d8(0x26b,'ihcj')]('账号['+this['name']+']开宝箱:\x20获得'+_0x33eafe[_0x1186d8(0x17f,'*upJ')][_0x1186d8(0x1e6,'EQin')]+_0x1186d8(0x205,'VOMW')+_0x33eafe[_0x1186d8(0x25c,'SAUS')][_0x1186d8(0x15a,'T[c]')][_0x1186d8(0x144,'4oGZ')]+'金币');continue;case'6':this[_0x1186d8(0x1c0,'h%kc')]=_0x33eafe[_0x1186d8(0x239,'7)v^')][_0x1186d8(0x1bc,']tPp')][_0x1186d8(0x2dd,'vi[9')];continue;}break;}}else _0x34a6bd[_0x1186d8(0x13c,'$nxM')]===_0x34a6bd['oJEoV']?_0x42e54a[_0x1186d8(0x19f,'gGId')](_0x1186d8(0x268,'%ykf')+this['name']+_0x1186d8(0x1b4,'T[c]')+_0x5019d2[_0x1186d8(0x225,'&C$M')]):$['logAndNotify']('账号['+this['name']+_0x1186d8(0x174,'4oGZ')+_0x33eafe[_0x1186d8(0x233,'sce2')]);}}catch(_0x353356){console[_0x1186d8(0x282,'r*F#')](_0x353356);}finally{return _0x34a6bd[_0x1186d8(0x2be,'GNuD')](_0x34a6bd[_0x1186d8(0x2f8,'T$fS')],_0x34a6bd[_0x1186d8(0x1a7,'Vn!k')])?_0x541683[_0x1186d8(0x21d,'!(Ai')](0x1):Promise[_0x1186d8(0x1f1,'8av#')](0x1);}}async[_0x2f0247(0x16c,'&C$M')](){const _0x3a0137=_0x2f0247,_0x57ac9d={'RGmlC':function(_0xb1f0f1,_0x189925){return _0xb1f0f1===_0x189925;},'fZRXO':_0x3a0137(0x253,'m]eg'),'dOnLk':function(_0x92c640,_0x262f35,_0x2d2b78,_0x42a8b9){return _0x92c640(_0x262f35,_0x2d2b78,_0x42a8b9);},'ciRMd':function(_0x57b9ea,_0x4abeb6,_0x36a019){return _0x57b9ea(_0x4abeb6,_0x36a019);},'XAKex':_0x3a0137(0x29d,'&C$M'),'zYHqW':_0x3a0137(0x22b,'5Fl$'),'bWggV':function(_0x7c0afb,_0x5b35e3){return _0x7c0afb==_0x5b35e3;},'wmfSB':'snQhz'};try{if(_0x57ac9d[_0x3a0137(0x26e,'5Fl$')](_0x57ac9d[_0x3a0137(0x189,'Ye1E')],'yrcrN'))return _0x2fec8d['resolve'](0x1);else{let _0x39c0b1=_0x3a0137(0x1f8,'$nxM')+this[_0x3a0137(0x1af,'h%kc')][_0x3a0137(0x15d,'gGId')]+_0x3a0137(0x25e,'pdRu')+this['param'][_0x3a0137(0x180,'tiyZ')]+_0x3a0137(0x260,'gGId'),_0x43d32e='{\x22task_key\x22:\x22excitation_ad_treasure_box\x22,\x22amount\x22:\x22'+this['score_amount']+'\x22,\x22ad_rit\x22:\x22'+this[_0x3a0137(0x280,'vi[9')]+'\x22,\x22ad_inspire\x22:\x22{\x22score_amount\x22:\x22'+this['score_amount']+_0x3a0137(0x2b2,'k!Q8')+this['amount']+_0x3a0137(0x1fe,'r*F#')+this[_0x3a0137(0x134,'ihcj')]+_0x3a0137(0x2cb,'a6z^'),_0x2bc763=_0x3a0137(0x178,'5Fl$')+this[_0x3a0137(0x263,'!(Ai')][_0x3a0137(0x199,'8av#')],_0x2dd071=_0x57ac9d['dOnLk'](populateUrlObject,_0x39c0b1,_0x2bc763,_0x43d32e);await _0x57ac9d['ciRMd'](httpRequest,_0x57ac9d[_0x3a0137(0x28a,'Vn!k')],_0x2dd071);let _0x27c3fa=httpResult;if(!_0x27c3fa)return;if(_0x27c3fa[_0x3a0137(0x133,'VOMW')]==_0x57ac9d[_0x3a0137(0x11c,'!(Ai')])await $['wait'](0x12c),await this['excitation_ad_treasure_box']();else _0x57ac9d['bWggV'](_0x27c3fa[_0x3a0137(0x1d8,'NtE]')],0x0)?$[_0x3a0137(0x28f,'vi[9')]('账号['+this['name']+_0x3a0137(0x15f,'vi[9')+_0x27c3fa[_0x3a0137(0x15e,'m]eg')][_0x3a0137(0x121,'8av#')]+'金币'):_0x57ac9d[_0x3a0137(0x12d,'o0]P')]===_0x57ac9d[_0x3a0137(0x26d,'jbuj')]?$['logAndNotify'](_0x3a0137(0x116,'r*F#')+this[_0x3a0137(0x114,'tiyZ')]+_0x3a0137(0x139,'T[c]')+_0x27c3fa[_0x3a0137(0x235,'5[mf')]):_0x3bdfd6[_0x3a0137(0x256,'tiyZ')]('账号['+this[_0x3a0137(0x2d3,']tPp')]+_0x3a0137(0x22e,'ihcj'));}}catch(_0x529ea6){console[_0x3a0137(0x128,'ihcj')](_0x529ea6);}finally{return Promise[_0x3a0137(0x254,'%ykf')](0x1);}}async['ad'](){const _0x131849=_0x2f0247,_0x107206={'GzOxP':_0x131849(0x2bf,'NtE]'),'dxVFP':function(_0xee5db6,_0x184fb9){return _0xee5db6===_0x184fb9;},'GoWgB':_0x131849(0x292,'8av#'),'hBjMb':_0x131849(0x2c8,'8av#'),'SvXxU':function(_0x459be9,_0x28559c,_0x40c82c,_0x3716cb){return _0x459be9(_0x28559c,_0x40c82c,_0x3716cb);},'AuIvL':_0x131849(0x257,'sce2'),'sazKj':function(_0x20e6ef,_0x2cc030){return _0x20e6ef==_0x2cc030;},'tRRhT':function(_0x53b632,_0x4cd303){return _0x53b632===_0x4cd303;},'jmyAZ':_0x131849(0x197,'OY(('),'PuRzg':function(_0x4f2062,_0x343473){return _0x4f2062===_0x343473;},'VJwfu':'fPyao','CflTO':function(_0x453c98,_0x55beb3){return _0x453c98===_0x55beb3;}};try{if(_0x107206[_0x131849(0x112,'FPOW')](_0x107206['GoWgB'],_0x107206[_0x131849(0x2e4,'sce2')]))return _0x1287ac[_0x131849(0x1dc,'FNga')](0x1);else{let _0x21444e=_0x131849(0x2cc,'GNuD')+this['param']['iid']+_0x131849(0x1aa,'FNga')+this['param'][_0x131849(0x194,'m]eg')]+_0x131849(0x222,'T[c]'),_0x256c5e=_0x131849(0x1c7,'sce2'),_0x4beee6=_0x131849(0x216,'NtE]')+this[_0x131849(0x14e,'ihcj')][_0x131849(0x269,'T[c]')],_0x42c356=_0x107206[_0x131849(0x258,'7)v^')](populateUrlObject,_0x21444e,_0x4beee6,_0x256c5e);await httpRequest(_0x107206[_0x131849(0x220,'ihcj')],_0x42c356);let _0x356101=httpResult;if(!_0x356101)return;await $[_0x131849(0x279,'4oGZ')](0xc8),_0x107206[_0x131849(0x1e8,'Ppiq')](_0x356101['err_no'],0x2717)&&(await $[_0x131849(0x1ee,'FPOW')](0x12c),await this['ad']()),_0x107206[_0x131849(0x2e3,'VOMW')](_0x356101[_0x131849(0x127,'k!Q8')],0x0)?_0x107206[_0x131849(0x1a0,'*uum')](_0x131849(0x12c,'a6z^'),_0x107206[_0x131849(0x2e0,'h%kc')])?($[_0x131849(0x227,'&C$M')]('账号['+this['name']+_0x131849(0x1f3,'#1)7')+_0x356101['data'][_0x131849(0x1bd,'Ye1E')]+'金币'),await $[_0x131849(0x2ef,'hiHY')](0x7530),await this[_0x131849(0x2c7,'a6z^')]()):_0x370273[_0x131849(0x236,'Vn!k')](_0x2bbd03):_0x107206['PuRzg'](_0x107206[_0x131849(0x2fe,'Ye1E')],_0x131849(0x190,'^@2!'))?$[_0x131849(0x153,'Ek^S')](_0x131849(0x1f4,'VOMW')+this['name']+_0x131849(0x2d7,'#1)7')+_0x356101[_0x131849(0x172,'Ppiq')]):(_0x436160[_0x131849(0x123,'^@2!')]=_0x638907,_0x42ac51[_0x131849(0x224,'k!Q8')][_0x107206['GzOxP']]=_0x131849(0x1f0,'9I$%'),_0xd6ce65['headers'][_0x131849(0x1b2,'&C$M')]=_0x590681[_0x131849(0x123,'^@2!')]?_0x3f1d8d[_0x131849(0x19a,'gGId')][_0x131849(0x217,'pdRu')]:0x0);}}catch(_0x2112aa){console['log'](_0x2112aa);}finally{if(_0x107206[_0x131849(0x2ed,'T[c]')](_0x131849(0x1e0,'Rfh#'),_0x131849(0x13a,'gGId')))_0x384ff9['logAndNotify']('账号['+this[_0x131849(0x12a,']8[d')]+']开宝箱:\x20'+_0x31db49[_0x131849(0x213,'o0]P')]);else return Promise[_0x131849(0x175,'^@2!')](0x1);}}async[_0x2f0247(0x1a8,']tPp')](){const _0x4c73e4=_0x2f0247,_0x4d2d2e={'ADUvI':function(_0x285e66,_0x3cc0f4,_0x14e3f5,_0xd6d336){return _0x285e66(_0x3cc0f4,_0x14e3f5,_0xd6d336);},'PdCeK':function(_0x3ddc5e,_0x5a3d68,_0x3270e1){return _0x3ddc5e(_0x5a3d68,_0x3270e1);},'lxTZj':function(_0x499868,_0x405b3a){return _0x499868==_0x405b3a;},'JeDRi':_0x4c73e4(0x206,'ITE$'),'vNQyi':function(_0x2dd45b,_0x35f8e5){return _0x2dd45b!==_0x35f8e5;},'zeKvg':_0x4c73e4(0x23f,'gGId'),'mAxoK':'UpoJl'};try{let _0x5be64a='https://aweme.snssdk.com/luckycat/aweme/v1/task/done/excitation_ad/one_more?_request_from=web&iid='+this[_0x4c73e4(0x2d5,'#1)7')][_0x4c73e4(0x1e4,'%ykf')]+_0x4c73e4(0x1b5,'%ykf')+this[_0x4c73e4(0x1be,'k!Q8')][_0x4c73e4(0x240,'hiHY')]+_0x4c73e4(0x179,'VOMW'),_0x50bfb6=_0x4c73e4(0x1b8,'#1)7'),_0x4a7f79=_0x4c73e4(0x271,'EQin')+this[_0x4c73e4(0x212,'GNuD')][_0x4c73e4(0x28b,']tPp')],_0x150755=_0x4d2d2e[_0x4c73e4(0x245,'FPOW')](populateUrlObject,_0x5be64a,_0x4a7f79,_0x50bfb6);await _0x4d2d2e[_0x4c73e4(0x1ff,'*o81')](httpRequest,_0x4c73e4(0x1ae,'gGId'),_0x150755);let _0x174ee1=httpResult;if(!_0x174ee1)return;await $['wait'](0xc8);if(_0x4d2d2e[_0x4c73e4(0x211,'Vn!k')](_0x174ee1[_0x4c73e4(0x27a,']8[d')],0x2717))await $['wait'](0x12c),await this[_0x4c73e4(0x2e1,'ITE$')]();else _0x4d2d2e['lxTZj'](_0x174ee1[_0x4c73e4(0x186,'5Fl$')],0x0)?_0x4d2d2e['JeDRi']==='Bakuu'?_0x1c3b59['logAndNotify'](_0x4c73e4(0x2bd,'5Fl$')+this[_0x4c73e4(0x2d9,'FNga')]+_0x4c73e4(0x2f6,'GNuD')+_0xa51df7[_0x4c73e4(0x2c1,'vi[9')]):$[_0x4c73e4(0x26b,'ihcj')](_0x4c73e4(0x274,'T[c]')+this[_0x4c73e4(0x1ef,'gGId')]+']广告追加:\x20获得'+_0x174ee1[_0x4c73e4(0x2af,'Rfh#')]['amount']+'金币'):$[_0x4c73e4(0x2cd,'EQin')]('账号['+this['name']+_0x4c73e4(0x185,'Rfh#')+_0x174ee1[_0x4c73e4(0x156,'5Fl$')]);}catch(_0x25e7be){_0x4d2d2e[_0x4c73e4(0x23c,'EQin')](_0x4d2d2e[_0x4c73e4(0x182,'Rfh#')],_0x4d2d2e['zeKvg'])?_0x2afe5f['logAndNotify']('账号['+this[_0x4c73e4(0x24d,'sce2')]+_0x4c73e4(0x27e,'OY((')):console[_0x4c73e4(0x265,'vi[9')](_0x25e7be);}finally{if(_0x4d2d2e[_0x4c73e4(0x1cb,'FPOW')]!==_0x4d2d2e[_0x4c73e4(0x14c,'EQin')])_0x6d1135[_0x4c73e4(0x2a6,'OY((')](_0x4c73e4(0x1d3,'Ye1E')+this[_0x4c73e4(0x159,'k!Q8')]+_0x4c73e4(0x24a,'r*F#')+_0x42d061[_0x4c73e4(0x17a,'ITE$')][_0x4c73e4(0x16b,'5[mf')]+'金币');else return Promise[_0x4c73e4(0x2ff,'T[c]')](0x1);}}}!(async()=>{const _0x20773a=_0x2f0247,_0x57d3c9={'ChdEr':_0x20773a(0x187,'K5#g'),'gxHxm':function(_0x54f779,_0x23491b){return _0x54f779!==_0x23491b;},'fFaas':_0x20773a(0x163,'jbuj'),'SUNam':'yVijW','iUUSI':function(_0x1bf8c6){return _0x1bf8c6();},'WRtrW':function(_0x2e295b,_0x34fdd8){return _0x2e295b<_0x34fdd8;},'dJlHP':_0x20773a(0x27f,'sce2'),'oxpNA':'nEymE'};if(_0x57d3c9[_0x20773a(0x11f,'jbuj')](typeof $request,_0x57d3c9['fFaas'])){}else{if(_0x20773a(0x1a6,'$nxM')===_0x57d3c9[_0x20773a(0x246,']8[d')]){if(!await checkEnv())return;await _0x57d3c9[_0x20773a(0x1de,'!(Ai')](sc);let _0x21cd0e=[],_0x46722d=userList[_0x20773a(0x2dc,'EQin')](_0x1a6f1b=>_0x1a6f1b['ckValid']);if(_0x46722d[_0x20773a(0x120,']tPp')]<0x2){$['logAndNotify'](_0x20773a(0x1cc,'jbuj')),_0x21cd0e=[];for(let _0x5da592 of _0x46722d){_0x20773a(0x16a,'Ppiq')==='EcKoK'?_0x21cd0e['push'](_0x5da592['my']()):_0x57f603[_0x20773a(0x252,'k!Q8')](_0x1949f1);}await Promise[_0x20773a(0x2e7,'h%kc')](_0x21cd0e),_0x46722d=_0x46722d[_0x20773a(0x142,'*o81')](_0x3ea62c=>_0x3ea62c[_0x20773a(0x192,'FPOW')]);if(_0x57d3c9[_0x20773a(0x1bb,'4oGZ')](_0x46722d[_0x20773a(0x295,'Ye1E')],0x2)){$[_0x20773a(0x160,'h%kc')](_0x20773a(0x2ec,'Ye1E')),_0x21cd0e=[];for(let _0x375e7a of _0x46722d['filter'](_0x151b1c=>_0x151b1c[_0x20773a(0x21e,'NtE]')])){const _0x473f3f=_0x57d3c9[_0x20773a(0x14b,'Ek^S')]['split']('|');let _0x5c6f9b=0x0;while(!![]){switch(_0x473f3f[_0x5c6f9b++]){case'0':_0x21cd0e[_0x20773a(0x2f4,'T[c]')](_0x375e7a[_0x20773a(0x242,'Ek^S')]());continue;case'1':await $[_0x20773a(0x21c,'!(Ai')](0xbb8);continue;case'2':_0x21cd0e[_0x20773a(0x20f,'pdRu')](_0x375e7a['ad']());continue;case'3':_0x21cd0e[_0x20773a(0x110,'5[mf')](_0x375e7a['sign_in']());continue;case'4':await $[_0x20773a(0x2ef,'hiHY')](0xbb8);continue;}break;}}await Promise['all'](_0x21cd0e);}}else{if(_0x57d3c9[_0x20773a(0x18b,'*uum')]===_0x20773a(0x2b0,'#1)7'))console[_0x20773a(0x2ad,'FPOW')](_0x20773a(0x285,'ITE$'));else return _0x5e4c25['resolve'](0x1);}await $[_0x20773a(0x23d,'m]eg')]();}else{_0x565d4f['log'](_0x57d3c9[_0x20773a(0x2b1,'K5#g')]);return;}}})()[_0x2f0247(0x14a,'B$xH')](_0x38dd20=>console[_0x2f0247(0x232,'h%kc')](_0x38dd20))[_0x2f0247(0x207,'#1)7')](()=>$[_0x2f0247(0x1bf,'a6z^')]());async function sc(){const _0x18342f=_0x2f0247,_0x11636f={'JmxgB':_0x18342f(0x2d6,'OY(('),'Wxfuh':_0x18342f(0x1a5,'h%kc'),'nIrlq':_0x18342f(0x136,'OY(('),'bJxBr':_0x18342f(0x2b5,'r*F#'),'kQIOp':function(_0x4b9da5,_0x1a3b5d,_0x311383){return _0x4b9da5(_0x1a3b5d,_0x311383);},'ZsaEw':_0x18342f(0x1ec,'a6z^'),'aDaxk':function(_0x1d92a5,_0x5a5032){return _0x1d92a5===_0x5a5032;},'ZsUgx':_0x18342f(0x1fd,'FNga')};try{if(_0x11636f[_0x18342f(0x229,'VOMW')]===_0x18342f(0x2bb,'FPOW')){let _0x13c8b9=_0x18342f(0x237,'sce2'),_0x135fd9='',_0x12ca88=_0x11636f['kQIOp'](populateUrlObject,_0x13c8b9,_0x135fd9);await httpRequest(_0x11636f[_0x18342f(0x2e6,'sce2')],_0x12ca88);let _0x3fef2d=httpResult;if(!_0x3fef2d)return;$[_0x18342f(0x22d,'4oGZ')]('\x0a'+_0x3fef2d[_0x18342f(0x25a,'ihcj')]+_0x18342f(0x132,'#1)7')+_0x3fef2d[_0x18342f(0x176,']tPp')]+'》'+_0x3fef2d['author']);var _0x2196c5=_0x3fef2d[_0x18342f(0x27d,'$nxM')];}else this['param']=_0x3359ec[_0x18342f(0x2ea,'a6z^')](_0x48fe65),this['ckValid']=!![];}catch(_0x5cf0c0){}finally{if(_0x11636f[_0x18342f(0x13f,'SAUS')](_0x18342f(0x1f9,'4oGZ'),_0x11636f['ZsUgx'])){let _0x2cbdd9=_0x1b65bc[_0x18342f(0x1d7,']tPp')]('//','/')[_0x18342f(0x124,'$nxM')]('/')[0x1],_0x27a22f={'url':_0x351700,'headers':{'Host':_0x2cbdd9,'cookie':_0x94a9c8,'User-Agent':_0xce8b44},'timeout':0x2710};return _0x2334c4&&(_0x27a22f[_0x18342f(0x148,'%ykf')]=_0x5a5461,_0x27a22f[_0x18342f(0x208,'FPOW')][_0x11636f[_0x18342f(0x2a9,'FPOW')]]=_0x11636f['Wxfuh'],_0x27a22f['headers'][_0x11636f[_0x18342f(0x2a4,'T[c]')]]=_0x27a22f[_0x18342f(0x296,']tPp')]?_0x27a22f['body'][_0x18342f(0x2c6,'5[mf')]:0x0),_0x27a22f;}else return Promise[_0x18342f(0x254,'%ykf')](0x1);}}function _0x21e9(_0x52d919,_0x41c887){const _0x2c2558=_0x2c25();return _0x21e9=function(_0x21e9ca,_0x148190){_0x21e9ca=_0x21e9ca-0x10b;let _0x127b62=_0x2c2558[_0x21e9ca];if(_0x21e9['cxWKmA']===undefined){var _0x11746e=function(_0x120539){const _0x5ec948='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/=';let _0x9bc53a='',_0x374519='';for(let _0x2caaea=0x0,_0x1f114a,_0x1bec6a,_0x13b933=0x0;_0x1bec6a=_0x120539['charAt'](_0x13b933++);~_0x1bec6a&&(_0x1f114a=_0x2caaea%0x4?_0x1f114a*0x40+_0x1bec6a:_0x1bec6a,_0x2caaea++%0x4)?_0x9bc53a+=String['fromCharCode'](0xff&_0x1f114a>>(-0x2*_0x2caaea&0x6)):0x0){_0x1bec6a=_0x5ec948['indexOf'](_0x1bec6a);}for(let _0x26b1e1=0x0,_0x152fd4=_0x9bc53a['length'];_0x26b1e1<_0x152fd4;_0x26b1e1++){_0x374519+='%'+('00'+_0x9bc53a['charCodeAt'](_0x26b1e1)['toString'](0x10))['slice'](-0x2);}return decodeURIComponent(_0x374519);};const _0xa25750=function(_0x11bd78,_0x15eea3){let _0x1a2458=[],_0x44ff8c=0x0,_0x28790a,_0x2197eb='';_0x11bd78=_0x11746e(_0x11bd78);let _0x217879;for(_0x217879=0x0;_0x217879<0x100;_0x217879++){_0x1a2458[_0x217879]=_0x217879;}for(_0x217879=0x0;_0x217879<0x100;_0x217879++){_0x44ff8c=(_0x44ff8c+_0x1a2458[_0x217879]+_0x15eea3['charCodeAt'](_0x217879%_0x15eea3['length']))%0x100,_0x28790a=_0x1a2458[_0x217879],_0x1a2458[_0x217879]=_0x1a2458[_0x44ff8c],_0x1a2458[_0x44ff8c]=_0x28790a;}_0x217879=0x0,_0x44ff8c=0x0;for(let _0x3359ec=0x0;_0x3359ec<_0x11bd78['length'];_0x3359ec++){_0x217879=(_0x217879+0x1)%0x100,_0x44ff8c=(_0x44ff8c+_0x1a2458[_0x217879])%0x100,_0x28790a=_0x1a2458[_0x217879],_0x1a2458[_0x217879]=_0x1a2458[_0x44ff8c],_0x1a2458[_0x44ff8c]=_0x28790a,_0x2197eb+=String['fromCharCode'](_0x11bd78['charCodeAt'](_0x3359ec)^_0x1a2458[(_0x1a2458[_0x217879]+_0x1a2458[_0x44ff8c])%0x100]);}return _0x2197eb;};_0x21e9['AUJEEh']=_0xa25750,_0x52d919=arguments,_0x21e9['cxWKmA']=!![];}const _0x4ebbfb=_0x2c2558[0x0],_0x1cf3a6=_0x21e9ca+_0x4ebbfb,_0x5c0506=_0x52d919[_0x1cf3a6];return!_0x5c0506?(_0x21e9['HwIfKG']===undefined&&(_0x21e9['HwIfKG']=!![]),_0x127b62=_0x21e9['AUJEEh'](_0x127b62,_0x148190),_0x52d919[_0x1cf3a6]=_0x127b62):_0x127b62=_0x5c0506,_0x127b62;},_0x21e9(_0x52d919,_0x41c887);}async function checkEnv(){const _0x41bb04=_0x2f0247,_0x540ca9={'LWrgn':function(_0x427352,_0x4478d8){return _0x427352===_0x4478d8;},'PZLLm':'XricF','vgGbG':function(_0x2468a4,_0x344135){return _0x2468a4===_0x344135;},'wojyc':_0x41bb04(0x177,'EQin')};if(userCookie){if(_0x540ca9[_0x41bb04(0x1ca,'GNuD')](_0x41bb04(0x188,'ITE$'),_0x540ca9[_0x41bb04(0x249,'!(Ai')]))return _0x5ee97d[_0x41bb04(0x24f,'Ek^S')](0x1);else{let _0x1824d1=envSplitor[0x0];for(let _0x45263e of envSplitor){if(userCookie['indexOf'](_0x45263e)>-0x1){_0x1824d1=_0x45263e;break;}}for(let _0x1a65f8 of userCookie['split'](_0x1824d1)){if(_0x540ca9[_0x41bb04(0x145,'5[mf')](_0x41bb04(0x261,'Ek^S'),_0x540ca9[_0x41bb04(0x1ad,'5Fl$')])){if(_0x1a65f8)userList['push'](new UserInfo(_0x1a65f8));}else return _0x51cd34[_0x41bb04(0x2ff,'T[c]')](0x1);}userCount=userList[_0x41bb04(0x275,'Vn!k')];}}else{console[_0x41bb04(0x10c,'EQin')](_0x41bb04(0x2fd,'Ye1E'));return;}return console[_0x41bb04(0x11d,'9I$%')](_0x41bb04(0x149,'m]eg')+userCount+_0x41bb04(0x287,'FNga')),!![];}function populateUrlObject(_0x5a7fde,_0x4a7d4d,_0x22d51d=''){const _0x136ab0=_0x2f0247,_0x1a6dc7={'wxYzS':function(_0x5014c3,_0x15cb50){return _0x5014c3!==_0x15cb50;},'JlSdV':_0x136ab0(0x1ab,'%ykf'),'nZtvB':_0x136ab0(0x165,'^@2!'),'BNbVM':'content-type','xSKvs':'application/json;\x20charset=utf-8','ttaHF':_0x136ab0(0x168,'ITE$')};let _0xeab3e5=_0x5a7fde['replace']('//','/')[_0x136ab0(0x173,'7)v^')]('/')[0x1],_0x153611={'url':_0x5a7fde,'headers':{'Host':_0xeab3e5,'cookie':_0x4a7d4d,'User-Agent':defaultUA},'timeout':0x2710};return _0x22d51d&&(_0x1a6dc7[_0x136ab0(0x164,'OY((')](_0x1a6dc7[_0x136ab0(0x231,'*upJ')],_0x1a6dc7['nZtvB'])?(_0x153611[_0x136ab0(0x29c,'SAUS')]=_0x22d51d,_0x153611[_0x136ab0(0x2da,'*uum')][_0x1a6dc7[_0x136ab0(0x21a,'7)v^')]]=_0x1a6dc7['xSKvs'],_0x153611[_0x136ab0(0x2f1,'jbuj')][_0x1a6dc7['ttaHF']]=_0x153611['body']?_0x153611['body'][_0x136ab0(0x1b0,'tiyZ')]:0x0):_0x2103b5['logAndNotify'](_0x136ab0(0x1b9,'K5#g')+this['name']+_0x136ab0(0x201,'pdRu')+_0x43efcb['err_tips'])),_0x153611;}function randomArr(_0x4fa791){const _0x20a4e2=_0x2f0247,_0x45bb14={'fuSOH':function(_0x67084a,_0x46e61e,_0x1b0b99){return _0x67084a(_0x46e61e,_0x1b0b99);},'KvypH':function(_0x26bbf1,_0x2e5b12){return _0x26bbf1*_0x2e5b12;}};return _0x4fa791[_0x45bb14['fuSOH'](parseInt,_0x45bb14[_0x20a4e2(0x2c4,'^@2!')](Math['random'](),_0x4fa791[_0x20a4e2(0x170,'4oGZ')]),0xa)];}async function httpRequest(_0xfdf393,_0x51de5f){const _0x3c6705=_0x2f0247,_0x227499={'IOAQW':function(_0x456a1f,_0x39cb57,_0x34b2e5){return _0x456a1f(_0x39cb57,_0x34b2e5);},'CaXpg':function(_0x2721f8,_0x15cc26){return _0x2721f8!==_0x15cc26;},'waZdY':_0x3c6705(0x12b,'4oGZ'),'Ghtmk':function(_0x10f2d1,_0x446f3d){return _0x10f2d1===_0x446f3d;},'wuIsZ':_0x3c6705(0x1b1,'B$xH'),'uWdsv':_0x3c6705(0x20b,'*uum'),'EsJFh':function(_0x3f9f33,_0x35bf8d){return _0x3f9f33==_0x35bf8d;},'nrBTg':_0x3c6705(0x27c,'vi[9'),'vmpei':_0x3c6705(0x1c6,'FNga'),'bwWiC':function(_0x57df13,_0x2d7a19){return _0x57df13!==_0x2d7a19;},'OLEci':function(_0x53b14e){return _0x53b14e();},'VoCQC':function(_0x2e2363,_0x438987){return _0x2e2363<_0x438987;},'WCXTh':_0x3c6705(0x2a5,'hiHY'),'SbWwq':_0x3c6705(0x291,'hiHY'),'GLRzt':_0x3c6705(0x2b8,'7)v^')};return httpResult=null,httpReq=null,httpResp=null,new Promise(_0x2ea520=>{const _0x29afb1=_0x3c6705,_0x1a6710={'ROYlV':function(_0x305542,_0x26353a){const _0x86532=_0x21e9;return _0x227499[_0x86532(0x150,'#1)7')](_0x305542,_0x26353a);},'MNeJD':_0x227499[_0x29afb1(0x2fa,'ITE$')]};_0x227499[_0x29afb1(0x223,'!(Ai')]===_0x227499['GLRzt']?(_0x159dcb[_0x29afb1(0x24c,'ITE$')](_0x29afb1(0x117,'m]eg')+this['name']+']今日金币收入:'+_0x1baa20['data'][_0x29afb1(0x204,'m]eg')][_0x29afb1(0x1a3,'r*F#')]+_0x29afb1(0x1fc,'ihcj')+_0x308ae4[_0x29afb1(0x1fb,'&C$M')][_0x29afb1(0x2a7,'FNga')]['amount2']/0x64+'元'),_0x1a6710[_0x29afb1(0x26c,'*o81')](_0x30576b['data']['income_data'][_0x29afb1(0x2de,'hiHY')],0x7530)?(this[_0x29afb1(0x17d,'jbuj')]=!![],this[_0x29afb1(0x266,'T$fS')]=!![]):_0x5eb389['logAndNotify'](_0x29afb1(0x262,'*upJ')+this[_0x29afb1(0x24b,'EQin')]+_0x29afb1(0x283,'5[mf'))):$[_0x29afb1(0x2a8,'K5#g')](_0xfdf393,_0x51de5f,async(_0x13610d,_0x2d1797,_0xc7aa13)=>{const _0x2a53f4=_0x29afb1,_0x3c1bfe={'TFtOc':function(_0x3b9ecf,_0x343ead,_0x5653ee){const _0x45135=_0x21e9;return _0x227499[_0x45135(0x214,'a6z^')](_0x3b9ecf,_0x343ead,_0x5653ee);}};if(_0x227499[_0x2a53f4(0x140,'FNga')](_0x2a53f4(0x1a2,'hiHY'),_0x227499[_0x2a53f4(0x1ce,'sce2')]))return _0x2c159a[_0x3c1bfe[_0x2a53f4(0x111,'VOMW')](_0x4a8d40,_0x3457d0['random']()*_0x5d6853[_0x2a53f4(0x2ae,']8[d')],0xa)];else try{if(_0x2a53f4(0x2f2,']8[d')!==_0x2a53f4(0x297,'Ek^S'))_0x284b31[_0x2a53f4(0x13d,'OY((')](_0x31205b);else{httpReq=_0x2d1797,httpResp=_0xc7aa13;if(_0x13610d)httpResult=JSON['parse'](_0x2d1797[_0x2a53f4(0x2fc,'o0]P')]);else{if(_0xc7aa13['body']){if(_0x227499[_0x2a53f4(0x2fb,'EQin')](_0x227499[_0x2a53f4(0x284,'Vn!k')],_0x227499[_0x2a53f4(0x209,'pdRu')]))_0x3535a9['log'](_0x1a6710['MNeJD']);else{if(_0x227499[_0x2a53f4(0x22f,'jbuj')](typeof _0xc7aa13[_0x2a53f4(0x1e7,'OY((')],_0x227499['nrBTg']))httpResult=_0xc7aa13['body'];else{if(_0x227499['Ghtmk'](_0x2a53f4(0x1a9,'h%kc'),_0x227499['vmpei']))_0x4969bc[_0x2a53f4(0x2f5,'5[mf')](_0x10451a);else try{httpResult=JSON[_0x2a53f4(0x278,'Ye1E')](_0xc7aa13[_0x2a53f4(0x126,'B$xH')]);}catch(_0x3bbf17){httpResult=_0xc7aa13['body'];}}}}}}}catch(_0x23f7c6){}finally{_0x227499['bwWiC'](_0x2a53f4(0x1b6,'*upJ'),_0x2a53f4(0x1c5,'Rfh#'))?(this[_0x2a53f4(0x1db,'ITE$')]=![],_0x2ea53a['logAndNotify'](_0x2a53f4(0x11b,']8[d')+this['index']+']CK格式错误')):_0x227499[_0x2a53f4(0x28c,'T[c]')](_0x2ea520);}});});}var version_ = 'jsjiami.com.v7';

////////////////////////////////////////////////////////////////////
function Env(name,env) {
    "undefined" != typeof process && JSON.stringify(process.env).indexOf("GITHUB") > -1 && process.exit(0);
    return new class {
        constructor(name,env) {
            this.name = name
            this.notifyStr = ''
            this.startTime = (new Date).getTime()
            Object.assign(this,env)
            console.log(`${this.name} 开始运行：`)
        }
        isNode() {
            return "undefined" != typeof module && !!module.exports
        }
        isQuanX() {
            return "undefined" != typeof $task
        }
        isSurge() {
            return "undefined" != typeof $httpClient && "undefined" == typeof $loon
        }
        isLoon() {
            return "undefined" != typeof $loon
        }
        getdata(t) {
            let e = this.getval(t);
            if (/^@/.test(t)) {
                const[, s, i] = /^@(.*?)\.(.*?)$/.exec(t),
                r = s ? this.getval(s) : "";
                if (r)
                    try {
                        const t = JSON.parse(r);
                        e = t ? this.lodash_get(t, i, "") : e
                    } catch (t) {
                        e = ""
                    }
            }
            return e
        }
        setdata(t, e) {
            let s = !1;
            if (/^@/.test(e)) {
                const[, i, r] = /^@(.*?)\.(.*?)$/.exec(e),
                o = this.getval(i),
                h = i ? "null" === o ? null : o || "{}" : "{}";
                try {
                    const e = JSON.parse(h);
                    this.lodash_set(e, r, t),
                    s = this.setval(JSON.stringify(e), i)
                } catch (e) {
                    const o = {};
                    this.lodash_set(o, r, t),
                    s = this.setval(JSON.stringify(o), i)
                }
            }
            else {
                s = this.setval(t, e);
            }
            return s
        }
        getval(t) {
            return this.isSurge() || this.isLoon() ? $persistentStore.read(t) : this.isQuanX() ? $prefs.valueForKey(t) : this.isNode() ? (this.data = this.loaddata(), this.data[t]) : this.data && this.data[t] || null
        }
        setval(t, e) {
            return this.isSurge() || this.isLoon() ? $persistentStore.write(t, e) : this.isQuanX() ? $prefs.setValueForKey(t, e) : this.isNode() ? (this.data = this.loaddata(), this.data[e] = t, this.writedata(), !0) : this.data && this.data[e] || null
        }
        send(m, t, e = (() => {})) {
            if(m != 'get' && m != 'post' && m != 'put' && m != 'delete') {
                console.log(`无效的http方法：${m}`);
                return;
            }
            if(m == 'get' && t.headers) {
                delete t.headers["content-type"];
                delete t.headers["Content-Length"];
            } else if(t.body && t.headers) {
                if(!t.headers["content-type"]) t.headers["content-type"] = "application/json";
            }
            if(this.isSurge() || this.isLoon()) {
                if(this.isSurge() && this.isNeedRewrite) {
                    t.headers = t.headers || {};
                    Object.assign(t.headers, {"X-Surge-Skip-Scripting": !1});
                }
                let conf = {
                    method: m,
                    url: t.url,
                    headers: t.headers,
                    timeout: t.timeout,
                    data: t.body
                };
                if(m == 'get') delete conf.data
                $axios(conf).then(t => {
                    const {
                        status: i,
                        request: q,
                        headers: r,
                        data: o
                    } = t;
                    e(null, q, {
                        statusCode: i,
                        headers: r,
                        body: o
                    });
                }).catch(err => console.log(err))
            } else if (this.isQuanX()) {
                t.method = m.toUpperCase(), this.isNeedRewrite && (t.opts = t.opts || {}, Object.assign(t.opts, {
                        hints: !1
                    })),
                $task.fetch(t).then(t => {
                    const {
                        statusCode: i,
                        request: q,
                        headers: r,
                        body: o
                    } = t;
                    e(null, q, {
                        statusCode: i,
                        headers: r,
                        body: o
                    })
                }, t => e(t))
            } else if (this.isNode()) {
                this.got = this.got ? this.got : require("got");
                const {
                    url: s,
                    ...i
                } = t;
                this.instance = this.got.extend({
                    followRedirect: false
                });
                this.instance[m](s, i).then(t => {
                    const {
                        statusCode: i,
                        request: q,
                        headers: r,
                        body: o
                    } = t;
                    e(null, q, {
                        statusCode: i,
                        headers: r,
                        body: o
                    })
                }, t => {
                    const {
                        message: s,
                        response: i
                    } = t;
                    e(s, i, i && i.body)
                })
            }
        }
        time(t) {
            let e = {
                "M+": (new Date).getMonth() + 1,
                "d+": (new Date).getDate(),
                "h+": (new Date).getHours(),
                "m+": (new Date).getMinutes(),
                "s+": (new Date).getSeconds(),
                "q+": Math.floor(((new Date).getMonth() + 3) / 3),
                S: (new Date).getMilliseconds()
            };
            /(y+)/.test(t) && (t = t.replace(RegExp.$1, ((new Date).getFullYear() + "").substr(4 - RegExp.$1.length)));
            for (let s in e)
                new RegExp("(" + s + ")").test(t) && (t = t.replace(RegExp.$1, 1 == RegExp.$1.length ? e[s] : ("00" + e[s]).substr(("" + e[s]).length)));
            return t
        }
        async showmsg() {
            if(!this.notifyStr) return;
            let notifyBody = this.name + " 运行通知\n\n" + this.notifyStr
            if($.isNode()){
                var notify = require('./sendNotify');
                console.log('\n============== 推送 ==============')
                await notify.sendNotify(this.name, notifyBody);
            } else {
                this.msg(notifyBody);
            }
        }
        logAndNotify(str) {
            console.log(str)
            this.notifyStr += str
            this.notifyStr += '\n'
        }
        msg(e = t, s = "", i = "", r) {
            const o = t => {
                if (!t)
                    return t;
                if ("string" == typeof t)
                    return this.isLoon() ? t : this.isQuanX() ? {
                        "open-url": t
                    }
                 : this.isSurge() ? {
                    url: t
                }
                 : void 0;
                if ("object" == typeof t) {
                    if (this.isLoon()) {
                        let e = t.openUrl || t.url || t["open-url"],
                        s = t.mediaUrl || t["media-url"];
                        return {
                            openUrl: e,
                            mediaUrl: s
                        }
                    }
                    if (this.isQuanX()) {
                        let e = t["open-url"] || t.url || t.openUrl,
                        s = t["media-url"] || t.mediaUrl;
                        return {
                            "open-url": e,
                            "media-url": s
                        }
                    }
                    if (this.isSurge()) {
                        let e = t.url || t.openUrl || t["open-url"];
                        return {
                            url: e
                        }
                    }
                }
            };
            this.isMute || (this.isSurge() || this.isLoon() ? $notification.post(e, s, i, o(r)) : this.isQuanX() && $notify(e, s, i, o(r)));
            let h = ["", "============== 系统通知 =============="];
            h.push(e),
            s && h.push(s),
            i && h.push(i),
            console.log(h.join("\n"))
        }
        getMin(a,b){
            return ((a<b) ? a : b)
        }
        getMax(a,b){
            return ((a<b) ? b : a)
        }
        padStr(num,length,padding='0') {
            let numStr = String(num)
            let numPad = (length>numStr.length) ? (length-numStr.length) : 0
            let retStr = ''
            for(let i=0; i<numPad; i++) {
                retStr += padding
            }
            retStr += numStr
            return retStr;
        }
        json2str(obj,c,encodeUrl=false) {
            let ret = []
            for(let keys of Object.keys(obj).sort()) {
                let v = obj[keys]
                if(v && encodeUrl) v = encodeURIComponent(v)
                ret.push(keys+'='+v)
            }
            return ret.join(c);
        }
        str2json(str,decodeUrl=false) {
            let ret = {}
            for(let item of str.split('&')) {
                if(!item) continue;
                let idx = item.indexOf('=')
                if(idx == -1) continue;
                let k = item.substr(0,idx)
                let v = item.substr(idx+1)
                if(decodeUrl) v = decodeURIComponent(v)
                ret[k] = v
            }
            return ret;
        }
        randomString(len,charset='abcdef0123456789') {
            let str = '';
            for (let i = 0; i < len; i++) {
                str += charset.charAt(Math.floor(Math.random()*charset.length));
            }
            return str;
        }
        randomList(a) {
            let idx = Math.floor(Math.random()*a.length)
            return a[idx]
        }
        wait(t) {
            return new Promise(e => setTimeout(e, t))
        }
        done(t = {}) {
            const e = (new Date).getTime(),
            s = (e - this.startTime) / 1e3;
            console.log(`\n${this.name} 运行结束，共运行了 ${s} 秒！`)
            if(this.isSurge() || this.isQuanX() || this.isLoon()) $done(t)
        }
    }(name,env)
}
