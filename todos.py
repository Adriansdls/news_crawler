import pandas as pd

t = pd.read_csv("all_together.csv")
t.to_csv("all_together_bup.csv")

diario = pd.read_csv("el_diario/data/el_diario_full.csv")
debate = pd.read_csv("el_debate/data/el_debate_full.csv")
ser = pd.read_csv("cadena_ser/data/cadena_ser_full.csv")

ser_ = ser[["fecha","seccion","titulo","texto","url"]]
ser_["newspaper"] = "cadena ser"

debate_ = debate[["date","seccion","title","text","url"]]
debate_["newspaper"] = "el debate"

diario_ = diario[["date","seccion","title","text","url"]]
diario_["newspaper"] = "el diario"

ser_.rename(columns={"fecha":"date","titulo":"title","texto":"text"}, inplace=True)

tods = pd.concat([ser_,debate_], axis=0)
tods = pd.concat([tods,diario_],axis=0)
tods.drop_duplicates(inplace=True)
tods.reset_index(drop=True,inplace=True)

tods.to_csv("all_together.csv")

print("{0} new links were added".format((len(tods) - len(t))))