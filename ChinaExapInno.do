
*********************1.IPC-based Exaptation Identification**********************
use C:\ExIn_data\1010\合并数据1028.dta,clear

* Clean IPC strings and extract the original patent application numbers.
* IPC1 may contain multiple semicolon-separated IPC codes; only the first three characters of each code are used.
gen strL focal_id = ustrtrim(申请号1)
gen strL __ipc1 = ustrupper(ustrtrim(IPC1))
gen strL __ipc2 = ustrupper(ustrtrim(IPC主2))
replace __ipc1 = subinstr(__ipc1, "；", ";", .)
replace __ipc1 = ustrregexra(__ipc1, "\s+", "")
replace __ipc2 = ustrregexra(__ipc2, "\s+", "")

* Generate the "IPC1 three-character code set". Remove duplicates, sort the codes alphanumerically, and separate them with semicolons (e.g., C25;G05;G06).

gen strL IPC1三字符集合 = ""
mata:
S = st_sdata(., "__ipc1")
R = J(rows(S), 1, "")
for (i=1; i<=rows(S); i++) {
    if (S[i]!="") {
        p = tokens(S[i], ";")
        q = J(1, 0, "")
        // Mata的tokens()会保留分隔符；跳过单独的";"标记
        for (j=1; j<=cols(p); j++) {
            if (p[j] != ";" & p[j] != "") {
                q = (q, substr(p[j], 1, 3))
            }
        }
        if (cols(q)>0) {
            q = uniqrows(sort(q', 1))'
            R[i] = invtokens(q, ";")
        }
    }
}
st_sstore(., "IPC1三字符集合", R)
end

* Generate the "IPC2 three-character code" and the numeric variable d3.
* 0 = At least one three-character IPC code matches; 1 = All three-character IPC codes differ.
* If the original IPC information is missing or no valid three-character IPC code can be extracted, d3 remains missing (.).

gen str3 IPC主2三字符 = substr(__ipc2, 1, 3) ///
    if ustrregexm(__ipc2, "^[A-H][0-9]{2}")

gen byte d3 = .
replace d3 = (strpos(";" + IPC1三字符集合 + ";", ///
    ";" + IPC主2三字符 + ";") == 0) ///
    if IPC主2三字符 != "" & IPC1三字符集合 != "" ///
    & ustrregexm(__ipc1, ///
      "^[A-H][0-9]{2}[^;]*(;[A-H][0-9]{2}[^;]*)*$")

label var d3 "IPC三字符跨类别引用：0=相同，1=不同"
drop __ipc1 __ipc2

****************************** 1.1 Exaptation3 *******************************
* Exaptation3 = sum(d3) / N_obs, requiring complete citation counts and no missing values in d3 

capture confirm numeric variable n_cite
if _rc {
    gen double n_cite_num = real(subinstr(ustrtrim(n_cite), ",", "", .))
}
else {
    gen double n_cite_num = n_cite
}

bysort focal_id: gen long N_obs = _N
bysort focal_id: egen long sum_d3 = total(d3)
bysort focal_id: egen long N_valid3 = count(d3)
bysort focal_id: egen long N_cite_valid = count(n_cite_num)
bysort focal_id: egen double n_min = min(n_cite_num)
bysort focal_id: egen double n_max = max(n_cite_num)

gen double Exaptation3 = sum_d3 / N_obs ///
    if focal_id != "" & N_valid3 == N_obs & N_cite_valid == N_obs ///
    & n_min == n_max & n_min == N_obs
format Exaptation3 %9.6f

count if missing(Exaptation3)  //2452

gen double ex3 = sum_d3 / N_obs
format ex3 %9.6f
drop N_valid3  N_cite_valid  n_min  n_max
sort 股票代码 申请号1

save C:\ExIn_data\1010\ex3-1028.dta,replace  //185749
tab d3, missing
count if missing(d3)
egen byte patent_tag = tag(focal_id)
count if patent_tag == 1 & focal_id != ""
summarize Exaptation3 if patent_tag == 1 & focal_id != ""
summarize ex3 if patent_tag == 1 & focal_id != ""
drop N_valid3  N_cite_valid  n_min  

use C:\ExIn_data\1010\ex3-1028.dta,clear


***************************** 1.2 Exaptation4 **********************************
use C:\ExIn_data\1010\ex3-1028.dta,clear  //185749
rename N_obs  N_obs3
gen strL __ipc1 = ustrupper(ustrtrim(IPC1))
gen strL __ipc2 = ustrupper(ustrtrim(IPC主2))
replace __ipc1 = subinstr(__ipc1, "；", ";", .)
replace __ipc1 = ustrregexra(__ipc1, "\s+", "")
replace __ipc2 = ustrregexra(__ipc2, "\s+", "")

gen strL IPC14字符集合 = ""
mata:
S = st_sdata(., "__ipc1")
R = J(rows(S), 1, "")
for (i=1; i<=rows(S); i++) {
    if (S[i]!="") {
        p = tokens(S[i], ";")
        q = J(1, 0, "")
       
        for (j=1; j<=cols(p); j++) {
            if (p[j] != ";" & p[j] != "") {
                q = (q, substr(p[j], 1, 4))
            }
        }
        if (cols(q)>0) {
            q = uniqrows(sort(q', 1))'
            R[i] = invtokens(q, ";")
        }
    }
}
st_sstore(., "IPC14字符集合", R)
end

gen str4 IPC主2四字符 = substr(__ipc2, 1, 4) ///
    if ustrregexm(__ipc2, "^[A-H][0-9]{2}[A-Z]")

gen byte d4 = .
replace d4 = (strpos(";" + IPC14字符集合 + ";", ///
    ";" + IPC主2四字符 + ";") == 0) ///
    if IPC主2四字符 != "" & IPC14字符集合 != "" ///
    & ustrregexm(__ipc1, ///
      "^[A-H][0-9]{2}[A-Z][^;]*(;[A-H][0-9]{2}[A-Z][^;]*)*$")

label var d4 "IPC4 pair indicator: 0=match, 1=no match"
drop __ipc1 __ipc2

capture confirm numeric variable n_cite
if _rc {
    gen double n_cite_num = real(subinstr(ustrtrim(n_cite), ",", "", .))
}
else {
    gen double n_cite_num = n_cite
}

bysort focal_id: gen long N_obs = _N
bysort focal_id: egen long sum_d4 = total(d4)
bysort focal_id: egen long N_valid4 = count(d4)
bysort focal_id: egen long N_cite_valid = count(n_cite_num)
bysort focal_id: egen double n_min = min(n_cite_num)
bysort focal_id: egen double n_max = max(n_cite_num)

gen double Exaptation4 = sum_d4 / N_obs ///
    if focal_id != "" & N_valid4 == N_obs & N_cite_valid == N_obs ///
    & n_min == n_max & n_min == N_obs
format Exaptation4 %9.4f

count if missing(Exaptation4)  //2452

gen double ex4 = sum_d4/N_obs
format ex4 %9.4f
drop N_valid4  N_cite_valid  n_min  n_max

sort 股票代码 申请号1

save ex34-1028.dta,replace  //185749

use ex34-1028.dta,clear
tab d4, missing
count if missing(d4)
egen byte patent_tag = tag(focal_id)
count if patent_tag == 1 & focal_id != ""
summarize ex4 if patent_tag == 1 & focal_id != ""

duplicates drop 申请号1, force  //41017
drop 被引证专利1 focal_id n_cite_num3  n_cite_num patent_tag   

drop Exaptation3 Exaptation4
save "ex34-1028patent.dta", replace  //41017


*****************************2.NEIC-based Distance******************************
use ex34-1028.dta,clear  //185749
gen byte   neic_pair_min  = .
gen double neic_pair_mean = .
clear mata

mata:
// Extract distinct valid NEIC codes from a semicolon-separated list
string rowvector get_codes(string scalar s)
{
    string rowvector v, out
    real scalar k
    v = tokens(subinstr(strupper(s), ";", " "))
    out = J(1, 0, "")
    for (k=1; k<=cols(v); k++) {
        if (strlen(v[k])==5 & strpos("ABCDEFGHIJKLMNOPQRSTUVWXYZ",substr(v[k],1,1))>0 & strtoreal(substr(v[k],2,4))<.) out = (out,v[k])
    }
    if (cols(out)>0) out = uniqrows(out')'
    return(out)
}


void calc_neic()
{
    string matrix S
    string rowvector A, B
    real matrix R
    real scalar i, j, k, d, dmin, total, m, n

    S = st_sdata(., ("NEIC1","NEIC2"))
    R = J(rows(S), 2, .)

    for (i=1; i<=rows(S); i++) {
        A = get_codes(S[i,1])
        B = get_codes(S[i,2])
        m = cols(A)
        n = cols(B)
        if (m>0 & n>0) {
            dmin = 3
            total = 0
            for (j=1; j<=m; j++) {
                for (k=1; k<=n; k++) {
                    if (A[j]==B[k]) d = 0
                    else if (substr(A[j],1,1)!=substr(B[k],1,1)) d = 3
                    else if (substr(A[j],1,3)!=substr(B[k],1,3)) d = 2
                    else d = 1
                    if (d<dmin) dmin = d
                    total = total+d
                }
            }
            R[i,1] = dmin
            R[i,2] = total/(m*n)
        }
    }
    st_store(., ("neic_pair_min","neic_pair_mean"), R)
}

calc_neic()
end

* Focal-patent-level averages across valid citing patent pairs
bysort focal_id: egen long neic_N = count(neic_pair_min)
bysort focal_id: egen double neic_focal_minavg = mean(neic_pair_min)
bysort focal_id: egen double neic_focal_meanavg = mean(neic_pair_mean)

sort 股票代码

* Check and save the complete patent-pair dataset
summarize neic_pair_min neic_pair_mean neic_focal_minavg neic_focal_meanavg
save "NEIC1028.dta", replace  //185749


************************export tables****************************

********patent-pair level********
use NEIC1028.dta,clear  //185749
sort 股票代码 公开公告号

* patent-level
duplicates drop 申请号1, force  //41017
summarize ex3 ex4 neic_focal_minavg neic_focal_meanavg

* ex3: three-digit IPC-based exaptation index
summarize ex3, detail
local med_ex3 = r(p50)

gen ex3_high = (ex3 > `med_ex3') if !missing(ex3)

summarize neic_focal_meanavg, detail
local med_neic = r(p50)
gen neic_high = (neic_focal_meanavg > `med_neic') if !missing(neic_focal_meanavg)

tab ex3_high neic_high, cell

spearman ex3 ex4 neic_focal_minavg neic_focal_meanavg





































