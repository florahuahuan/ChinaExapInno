
***Split the cited patents
use "C:\ExIn_data\mfinal_small.dta", clear
sort 申请号
duplicates drop 公开公告号 申请号, force   //173715obs 
keep 序号 公开公告号 申请号 引证专利 被引证专利 IPC主分类 IPC 国民经济分类 申请日 公开公告日
destring 申请日, replace
format 申请日 %td
gen 申请年份 = year(申请日)
destring 公开公告日, replace
format 公开公告日 %td
gen 公开公告年份 = year(公开公告日)
drop 申请日 公开公告日

split 引证专利, parse(";")
rename 引证专利 引证专利原文
gen cite_raw = 引证专利原文
gen n_cite = 0
replace n_cite = 1 + length(cite_raw) - length(subinstr(cite_raw, ";", "", .)) if cite_raw != ""

***expand each record based on the actual number of cited patents
gen rowid = _n
expand n_cite
bysort rowid: gen 引证序号 = _n
gen work = cite_raw
gen 引证专利 = ""

forvalues k = 1/118 {
    replace 引证专利 = trim(substr(work, 1, strpos(work + ";", ";") - 1)) if 引证序号 == `k'
    replace work = substr(work, strpos(work + ";", ";") + 1, .) if 引证序号 >= `k'
}

keep 序号 公开公告号 申请号 IPC主分类 IPC  国民经济分类 引证专利原文 被引证专利 申请年份 公开公告年份 引证专利 n_cite
sort 公开公告号
order 引证专利, before (引证专利原文)
order n_cite,before(引证专利)  
order 国民经济分类,after(引证专利原文)
count if !missing(引证专利) // 476,371

**The expanded records were matched with other patent datasets.专利合并-匹配.dta
rename 公开公告号 公开公告号1
rename 申请号 申请号1
rename IPC主分类 IPC主分类1
rename IPC IPC1
rename 引证专利 引证专利1
rename 引证专利原文 引证专利原文1
rename 国民经济分类 国民经济分类1   
rename 申请年份 申请年份1
rename 公开公告年份 公开公告年份1
rename 引证专利1 公开公告号2  //Cited patent (Dataset 1) = Patent publication number (Dataset 2)
merge m:1 公开公告号2  using C:\ExIn_data\2\专利合并-匹配.dta
keep if _merge==3
drop _merge
rename 申请年份1 apyear1
rename 公开公告年份1 puyear1
order apyear1,after(申请号1)
order apyear2,after(apyear1)
save C:\ExIn_data\2\专利匹配数据7.14.dta,replace //468429

/********************************************************************
Mastrogiorgio and Gilsing-style Exaptation Index

early_patent_id  = earlier focal/cited patent i
late_patent_id   = later citing patent j

d3/d4 = citation-link-level dummy
yj3/yj4 = focal-patent-level proportion
********************************************************************/
use "C:\ExIn_data\专利匹配数据7.14.dta", clear
keep 公开公告号1 申请号1 IPC主分类1 IPC1 ///
     公开公告号2 ipc主分类2 ipc2
rename 公开公告号1   late_patent_id
rename 申请号1       late_application_id
rename IPC主分类1    late_ipc_main
rename IPC1          late_ipc_all
rename 公开公告号2   early_patent_id
rename ipc主分类2    early_ipc_main
rename ipc2          early_ipc_all

describe late_patent_id early_patent_id ///
         late_ipc_main early_ipc_main early_ipc_all

drop if missing(late_patent_id) | missing(early_patent_id)
drop if missing(late_ipc_main)  | missing(early_ipc_main)

duplicates report early_patent_id late_patent_id
duplicates drop early_patent_id late_patent_id, force

foreach v in late_ipc_main early_ipc_main early_ipc_all {

    replace `v' = upper(strtrim(`v'))
    replace `v' = subinstr(`v', " ", "", .)

    replace `v' = subinstr(`v', "；", ";", .)
    replace `v' = subinstr(`v', "，", ";", .)
    replace `v' = subinstr(`v', ",",  ";", .)
    replace `v' = subinstr(`v', "|",  ";", .)

    while strpos(`v', ";;") > 0 {
        replace `v' = subinstr(`v', ";;", ";", .)
    }

    replace `v' = substr(`v', 2, .) ///
        if substr(`v', 1, 1) == ";"

    replace `v' = substr(`v', 1, strlen(`v') - 1) ///
        if substr(`v', strlen(`v'), 1) == ";"
}

* Extract three-digit and four-digit IPC classifications
* H04L12/02 -> H04(three-digit/class)
* H04L12/02 -> H04L(four-digit/subclass)
gen str3 late_or3  = substr(late_ipc_main,  1, 3)
gen str4 late_or4  = substr(late_ipc_main,  1, 4)

gen str3 early_or3 = substr(early_ipc_main, 1, 3)
gen str4 early_or4 = substr(early_ipc_main, 1, 4)

replace late_or3  = "" if strlen(late_or3)  < 3
replace late_or4  = "" if strlen(late_or4)  < 4
replace early_or3 = "" if strlen(early_or3) < 3
replace early_or4 = "" if strlen(early_or4) < 4

* compare citing patent OR & focal patent OR
* anticipated=1 indicates later OR emerge earlier OR/XR 
* anticipated=0 indicates no
gen byte anticipated3 = 0 ///
    if late_or3 != "" & early_or3 != ""
gen byte anticipated4 = 0 ///
    if late_or4 != "" & early_or4 != ""
replace anticipated3 = 1 ///
    if late_or3 == early_or3 ///
    & late_or3 != "" & early_or3 != ""
replace anticipated4 = 1 ///
    if late_or4 == early_or4 ///
    & late_or4 != "" & early_or4 != ""

* split earlier focal patent IPC all
* early_ipc_all includes focal patent  main IPC and other IPC
capture drop eipc*
split early_ipc_all, parse(";") gen(eipc)
ds eipc*
local early_ipcs `r(varlist)'

* compare later citing patent OR & earlier focal patent IPC（OR + XR）
foreach v of local early_ipcs {

    replace `v' = upper(strtrim(`v'))
    replace `v' = subinstr(`v', " ", "", .)

    * three-digit IPC
    replace anticipated3 = 1 ///
        if substr(`v', 1, 3) == late_or3 ///
        & strlen(`v') >= 3 ///
        & late_or3 != ""

    * four-digit IPC
    replace anticipated4 = 1 ///
        if substr(`v', 1, 4) == late_or4 ///
        & strlen(`v') >= 4 ///
        & late_or4 != ""
}

* construct citation-link-level dummy d_ij
* d=1：later citing patent OR != earlier focal patent OR and all XR
gen byte d3 = (anticipated3 == 0) ///
    if late_or3 != "" & early_or3 != ""
gen byte d4 = (anticipated4 == 0) ///
    if late_or4 != "" & early_or4 != ""
label variable d3 ///
    "Pair-level exaptation dummy: three-digit IPC"
label variable d4 ///
    "Pair-level exaptation dummy: four-digit IPC"
label define yesno 0 "No" 1 "Yes"
label values d3 yesno
label values d4 yesno
tab d3, missing
tab d4, missing
tab d3 d4, row column missing

* aggregate earlier focal/cited patent 
* yj = qualifying forward citations / all eligible forward citations
* three-digit IPC
bysort early_patent_id: egen N3 = count(d3)
bysort early_patent_id: egen exap_links3 = total(d3)
gen double yj3 = exap_links3 / N3 if N3 > 0

* four-digit IPC
bysort early_patent_id: egen N4 = count(d4)
bysort early_patent_id: egen exap_links4 = total(d4)
gen double yj4 = exap_links4 / N4 if N4 > 0

label variable N3 ///
    "Eligible forward citations: three-digit calculation"
label variable N4 ///
    "Eligible forward citations: four-digit calculation"
label variable exap_links3 ///
    "Exaptation-classified forward citations: three-digit IPC"
label variable exap_links4 ///
    "Exaptation-classified forward citations: four-digit IPC"
label variable yj3 ///
    "Patent-level Exaptation Index: three-digit IPC"
label variable yj4 ///
    "Patent-level Exaptation Index: four-digit IPC"
format yj3 yj4 %9.4f
rename late_patent_id   公开公告号1
rename late_application_id 申请号1
rename late_ipc_main    IPC主分类1    
rename late_ipc_all     IPC1
rename early_patent_id   公开公告号2
rename early_ipc_main    ipc主分类2    
rename early_ipc_all    ipc2   
rename yj3  ex3
rename yj4  ex4
keep 公开公告号1 申请号1 IPC主分类1 IPC1 公开公告号2 ipc主分类2 ipc2 ex3 ex4
save mas.dta,replace  //464949

****************NEIC distance******************************************
use C:\ExIn_data\专利匹配数据7.14.dta,clear  //468429
keep 序号 公开公告号1 申请号1 引证专利原文1 国民经济分类1 公开公告号2 国民经济分类2
sort 公开公告号1   
***average vallue
rename 公开公告号1 pat_i
rename 国民经济分类1 codes_i
rename 公开公告号2 pat_j
rename 国民经济分类2 codes_j
gen long pairid = _n

***Clean strings
replace codes_i = upper(strtrim(codes_i))
replace codes_j = upper(strtrim(codes_j))

***Replace semicolons with spaces to facilitate the use of wordcount() and word().
replace codes_i = subinstr(codes_i, "; ", " ", .)
replace codes_i = subinstr(codes_i, ";",  " ", .)

replace codes_j = subinstr(codes_j, "; ", " ", .)
replace codes_j = subinstr(codes_j, ";",  " ", .)  //46w

***split i
preserve
keep pairid pat_i pat_j codes_i 申请号1
gen n_i = wordcount(codes_i)
drop if missing(n_i) | n_i == 0
expand n_i
bysort pairid: gen k_i = _n
gen code_i = word(codes_i, k_i)
replace code_i = strtrim(code_i)
drop if missing(code_i) | code_i == ""
duplicates drop pairid code_i, force
keep pairid pat_i pat_j code_i 申请号1
save long_i_temp.dta, replace
restore   //468w

***split j
preserve
keep pairid pat_i pat_j codes_j 申请号1
gen n_j = wordcount(codes_j)
drop if missing(n_j) | n_j == 0
expand n_j
bysort pairid: gen k_j = _n
gen code_j = word(codes_j, k_j)
replace code_j = strtrim(code_j)
drop if missing(code_j) | code_j == ""
duplicates drop pairid code_j, force
keep pairid pat_i pat_j code_j 申请号1
save long_j_temp.dta, replace
restore  //468w

***same pairid code_i × code_j 
use long_i_temp.dta, clear
joinby pairid using long_j_temp.dta   //6231w

***calculate dist
gen sec_i = substr(code_i, 1, 1)
gen big_i = substr(code_i, 2, 2)
gen sec_j = substr(code_j, 1, 1)
gen big_j = substr(code_j, 2, 2)
gen dist = .
replace dist = 0 if code_i == code_j
replace dist = 1 if sec_i == sec_j & big_i == big_j & code_i != code_j
replace dist = 2 if sec_i == sec_j & big_i != big_j
replace dist = 3 if sec_i != sec_j

***pairid min
bysort pairid: egen prodis_min = min(dist)

***pairid mean
bysort pairid: egen pair_prodis_mean = mean(dist)  //6231w  

***Keep only one record for each (i, j) pair.
bysort pairid: keep if _n == 1 //46w

bysort pat_i: egen pat_prodist_mean = mean(pair_prodis_mean)
sort pat_i
rename pat_i 公开公告号1 
rename pat_j 公开公告号2 

keep 公开公告号1 公开公告号2 申请号1 prodis_min pair_prodis_mean dist
rename prodis_min neic_min 
rename pair_prodis_mean  neic_mean

save neic.dta,replace   //468056

/********************************************************************
Merge the three datasets to create the patent-level dataset.
专利匹配数据7.14.dta, clear  // 468,429 records
mas.dt.dta, replace   // 464,949 records
neic7-16.dta, replace  // 468,056 records
********************************************************************/
use C:\ExIn_data\2\专利匹配数据7.14.dta, clear
merge 1:1 公开公告号1  公开公告号2 using "mas.dta"
keep if _merge==3
drop _merge   //464949
merge 1:1 公开公告号1  公开公告号2 using "neic.dta"
keep if _merge==3
drop _merge 
save patent.dta,replace  //464949

************merge pair-level+firm data*********************
use C:\ExIn_data\上市公司专利2023.dta, replace //208w
rename 专利申请号 申请号1
duplicates drop 股票代码 申请号1, force  
duplicates drop 申请号1, force  
merge 1:m 申请号1  using "patent.dta"
keep if _merge==3
drop _merge  
sort 股票代码 
drop dist 专利申请年份 IPC分类号 puyear1 puyear2 
drop 序号 n_cite
drop apyear1 apyear2 引证专利原文1
drop 被引证专利
rename 股票代码     stock_code
rename 专利类型     fp_type
rename 申请号1      fpan
rename 公开公告号1  fppn
rename IPC主分类1   fpipc_main
rename IPC1         fpipc_all
rename 公开公告号2   cppn
rename 国民经济分类1  fp_neic
rename ipc主分类2     cpipc_main
rename ipc2           cpipc_all
rename 国民经济分类2   cp_neic
rename ex3            Exaptation3
rename ex4            Exaptation4
rename neic_min       neicdis_min
rename neic_mean      neicdis_mean

label var stock_code  "identifier firm associated with the focal patent"
label var fpan        "Focal patent application Number"
label var fppn       "Focal patent publication number"
label var fpipc_main "Focal patent Main IPC class"
label var fpipc_all  "Focal patent all IPC class"
label var fp_neic    "Focal patent Industry classification (NEIC)"
label var fp_type    "Type of focal patent (e.g., invention, utility model, design)"
label var cppn       "Citing patent publication number"
label var cpipc_main "Citing patent Main IPC class"
label var cpipc_all  "Citing patent all IPC class"
label var cp_neic    "Citing patent Industry classification (NEIC)"
label var Exaptation3 "IPC-based exaptation index (three-digit IPC level)"
label var Exaptation4 "IPC-based exaptation index (four-digit IPC level)"
label var neicdis_min "Minimum NEIC distance between cited and citing patents"
label var neicdis_mean "Average NEIC distance between cited and citing patents"
save C:\ExIn_data\ChinaExapInno.dta,replace 

use C:\ExIn_data\ChinaExapInno.dta,clear








