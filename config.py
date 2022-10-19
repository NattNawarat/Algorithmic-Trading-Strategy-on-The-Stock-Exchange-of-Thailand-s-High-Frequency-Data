from re import S
from turtle import st


stocks_list = {}
#.CONSUMP
stocks_list["FASHION"] = ["AFC","BTNC","CPH","CPL","ICC","NC","PAF","PDJ","PG","SABINA","SAWANG","SUC","TNL","TR","TTI","TTT","UPF","UT","WACOAL","WFX",]
stocks_list["HOME"] = ["AJA","DTCI","FANCY","KYE","L&E","MODERN","OGC","ROCK","SIAM","TCMC","TSR"]
stocks_list["PERSON"] = ["APCO","DDD","JCT","KISS","NV","OCC","STGT","STHAI","TNR","TOG",]
stocks_list["CONSUMP"] = stocks_list["FASHION"] + stocks_list["HOME"]

#.AGRO
stocks_list["AGRI"] = ["EE", "GFPT", "LEE", "MAX", "NER", "PPPM", "STA", "TFM", "TRUBB", "TWPC", "UPOIC", "UVAN", "VPO"]
stocks_list["FOOD"] = ["APURE", "ASIAN", "BR", "BRR", "CBG", "CFRESH", "CHOTI", "CM", "CPF", "CPI", "F&D", "GLOCON", "HTC", "ICHI", "KBS", "KSL", "KTIS", "LST", "M", "MALEE", "MINT", "NRF", "NSL", "OISHI", "OSP", "PB", "PM", "PRG", "RBF", "SAPPE", "SAUCE", "SFP", "SNNP", "SNP", "SORKON", "SSC", "SSF", "SST", "SUN", "TC", "TFG", "TFMAMA", "TIPCO", "TKN", "TU", "TVO", "W", "ZEN"]
stocks_list["AGRO"] = stocks_list["AGRI"] + stocks_list["FOOD"]

#.FINCIAL
stocks_list["BANK"] = ["BAY", "BBL", "CIMBT", "KBANK", "KKP", "KTB", "LHFG", "SCB", "TCAP", "TISCO", "TMB"]
stocks_list["FIN"] = ["AEONTS", "AMANAH", "ASAP", "ASK", "ASP", "BAM", "BFIT", "BYD", "CGH", "CHAYO", "ECL", "FNS", "FSS", "GBX", "GL", "HENG", "IFS", "JMT", "KCAR", "KGI", "KTC", "MFC", "MICRO", "ML", "MST", "MTC", "NCAP", "PE", "PL", "S11", "SAK", "SAWAD", "THANI", "TIDLOR", "TK", "TNITY", "UOBKH", "XPG"]
stocks_list["INSUR"] = ["AYUD","BKI","BLA","BUI","CHARAN","INSURE","KWI","MTI","NKI","NSI","SMK","TGH","THRE","THREL","TIP","TQM","TSI","TVI",]
stocks_list["FINCIAL"] = stocks_list["BANK"] + stocks_list["FIN"] + stocks_list["INSUR"]

#INDUS
stocks_list["AUTO"] = ["3K-BAT","ACG","AH","CWT","EASON","GYT","HFT","IHL","INGRS","IRC","PCSGH","SAT","SPG","STANLY","TKT","TNPC","TRU","TSC",]
stocks_list["IMM"] = ["ALLA","ASEFA","CPT","CRANE","CTW","FMT","HTECH","KKC","PK","SNC","STARK","TCJ","TPCS","VARO",]
stocks_list["PAPER"] = ["UTP",]
stocks_list["PETRO"] = ["BCT","CMAN","GC","GGC","GIFT","IVL","NFC","PATO","PMTA","PTTGC","SUTHA","TCCC","TPA","UAC","UP","VNT",]
stocks_list["PKG"] = ["AJ","ALUCON","BGC","CSC","NEP","PTL","SCGP","SFLEX","SITHAI","SLP","SMPC","SPACK","TCOAT","TFI","THIP","TMD","TOPP","TPAC","TPBI","TPP",]
stocks_list["STEEL"] = ["2S","AMC","BSBM","CEN","CITY","CSP","GJS","GSTEEL","INOX","LHK","MCS","MILL","NOVA","PAP","PERM","SAM","SMIT","SSSC","TGPRO","THE","TMT","TSTH","TWP","TYCN",]
stocks_list["INDUS"] = stocks_list["AUTO"] + stocks_list["IMM"] + stocks_list["PAPER"] + stocks_list["PETRO"] + stocks_list["PKG"] + stocks_list["STEEL"]

#RESOURCE
stocks_list["ENERG"] = ["7UP", "ABPIF", "ACC", "ACE", "AGE", "AI", "AIE", "AKR", "BAFS", "BANPU", "BCP", "BCPG", "BGRIM", "BPP", "BRRGIF", "CKP", "CV", "DEMCO", "EA", "EASTW", "EGATIF", "EGCO", "EP", "ESSO", "ETC", "GPSC", "GREEN", "GULF", "GUNKUL", "IFEC", "IRPC", "KBSPIF", "LANNA", "MDX", "OR", "PRIME", "PTG", "PTT", "PTTEP", "QTC", "RATCH", "RPC", "SCG", "SCI", "SCN", "SGP", "SKE", "SOLAR", "SPCG", "SPRC", "SSP", "SUPER", "SUPEREIF", "SUSCO", "TAE", "TCC", "TOP", "TPIPP", "TSE", "TTW", "UBE", "WHAUP", "WP"]
stocks_list["MINE"] = ["TNL"]
stocks_list["RESOURC"] =  stocks_list["ENERG"] + stocks_list["MINE"]

#SERVICE
stocks_list["HELTH"] = ["AHC", "BCH", "BDMS", "BH", "CHG", "CMR", "EKH", "KDH", "LPH", "M-CHAI", "NEW", "NTV", "PR9", "PRINC", "RAM", "RJH", "RPH", "SKR", "SVH", "THG", "VIBHA", "VIH", "WPH"]
stocks_list["COMM"] = ["B52","BEAUTY","BIG","BJC","COM7","CPALL","CPW","CRC","CSS","DOHOME","FN","FTE","GLOBAL","HMPRO","ILM","IT","KAMART","LOXLEY","MAKRO","MC","MEGA","MIDA","RS","RSP","SABUY","SCM","SINGER","SPC","SPI","SVT",]
stocks_list["MEDIA"] = ["AMARIN","AQUA","AS","BEC","FE","GPI","GRAMMY","JKN","MACO","MAJOR","MATCH","MATI","MCOT","MONO","MPIC","NMG","ONEE","PLANB","POST","PRAKIT","SE-ED","TBSP","TH","TKS","VGI","WAVE","WORK",]
stocks_list["PROF"] = ["BWG","GENCO","PRO","SISB","SO",]
stocks_list["TOURISM"] = ["ASIA","BEYOND","CENTEL","CSR","DUSIT","ERW","GRAND","LRH","MANRIN","OHTL","ROH","SHANG","SHR","VRANDA",]
stocks_list["TRANS"] = ["AAV","AOT","ASIMAR","B","BA","BEM","BTS","BTSGIF","DMT","III","JUTHA","JWD","KEX","KIAT","KWC","MENA","NOK","NYT","PORT","PRM","PSL","RCL","TFFIF","THAI","TSTE","TTA","WICE",]
stocks_list["SERVICE"] = stocks_list["HELTH"] + stocks_list["COMM"] + stocks_list["MEDIA"] + stocks_list["PROF"] + stocks_list["PROF"] + stocks_list["TOURISM"] + stocks_list["TRANS"]

#TECH
stocks_list["ETRON"] = ["CCET","DELTA","HANA","KCE","METCO","NEX","SMT","SVI","TEAM",]
stocks_list["ICT"] = ["ADVANC","AIT","ALT","AMR","BLISS","DIF","DTAC","FORTH","HUMAN","ILINK","INET","INTUCH","ITEL","JAS","JASIF","JMART","JR","JTS","MFEC","MSC","PT","SAMART","SAMTEL","SDC","SIS","SKY","SVOA","SYMC","SYNEX","THCOM","TKC","TRUE","TWZ",]
stocks_list["TECH"] = stocks_list["ETRON"] + stocks_list["ICT"]

#SET50
stocks_list["SET50"] = ["7UP", "ABPIF", "ACC", "ACE", "AGE", "AI", "AIE", "AKR", "BAFS", "BANPU", "BCP", "BCPG", "BGRIM", "BPP", "BRRGIF", "CKP", "CV", "DEMCO", "EA", "EASTW", "EGATIF", "EGCO", "EP", "ESSO", "ETC", "GPSC", "GREEN", "GULF", "GUNKUL", "IFEC", "IRPC", "KBSPIF", "LANNA", "MDX", "OR", "PRIME", "PTG", "PTT", "PTTEP", "QTC", "RATCH", "RPC", "SCG", "SCI", "SCN", "SGP", "SKE", "SOLAR", "SPCG", "SPRC", "SSP", "SUPER", "SUPEREIF", "SUSCO", "TAE", "TCC", "TOP", "TPIPP", "TSE", "TTW", "UBE", "WHAUP", "WP"]



data_feed_path = "/*YOUR SYSTEM PATH*/DataFeed"
result_feed_path = "/*YOUR SYSTEM PATH*/ResultFeed"
sector_price_path = "/*YOUR SYSTEM PATH*/SectorPrice"
comission = 0.0007