! E0-DYN closure
!
Exogenous
    af
    afe(ENDWC_COMM,PROD_COMM,REG) 
    afereg
    afesec
    ams !added!
    ao
    atall 
    atm 
    atf 
    ats 
    atd 
    au
    avadiff
    avareg
    ! bfe(ENDWNA_COMM,PROD_COMM,REG) 
    ! bfereg
    dpgov
    dppriv
    dpsave
    empl
    endwslack
    incomeslack
    pop
    profitslack
    psavewld
    qfactsup(ENDWNA_COMM,REG)
    SDKHAT
    SDRORT
    SDRORW
    SDTBALWORLD
    sqcgdsworld
    sqk
    sqkworld
    srorge
    swq_f
    swqh
    swqhf
    swqht
    time
    tm
    tms
    to
    tp
    tradslack
    tx
    txs
    tf tpm tpd tgm tgd tfm tfd
    ;
!
Rest Endogenous;

!Swap DKHAT = SDKHAT ;
!Swap wqht = swqht ;
!Swap dpsave("ZAF") = DTBALR("ZAF");

! FIXED WAGE CLOSURE: endogenise unskilled labour endowment and fix real wage
!Swap qfactsup("UnSkLab",REG) = pfactreal("UnSkLab",REG);
Swap qfactsup("UnSkLab","egy") = pfactreal("UnSkLab","egy");
Swap qfactsup("UnSkLab","RestofAfrica") = pfactreal("UnSkLab","RestofAfrica");
Swap qfactsup("UnSkLab","xnf") = pfactreal("UnSkLab","xnf");
Swap qfactsup("UnSkLab","xac") = pfactreal("UnSkLab","xac");
Swap qfactsup("UnSkLab","eth") = pfactreal("UnSkLab","eth");
Swap qfactsup("UnSkLab","ken") = pfactreal("UnSkLab","ken");
Swap qfactsup("UnSkLab","mdg") = pfactreal("UnSkLab","mdg");
Swap qfactsup("UnSkLab","mwi") = pfactreal("UnSkLab","mwi");
Swap qfactsup("UnSkLab","mus") = pfactreal("UnSkLab","mus");
Swap qfactsup("UnSkLab","moz") = pfactreal("UnSkLab","moz");
Swap qfactsup("UnSkLab","rwa") = pfactreal("UnSkLab","rwa");
Swap qfactsup("UnSkLab","tza") = pfactreal("UnSkLab","tza");
Swap qfactsup("UnSkLab","uga") = pfactreal("UnSkLab","uga");
Swap qfactsup("UnSkLab","zmb") = pfactreal("UnSkLab","zmb");
Swap qfactsup("UnSkLab","zwe") = pfactreal("UnSkLab","zwe");
Swap qfactsup("UnSkLab","xec") = pfactreal("UnSkLab","xec");
Swap qfactsup("UnSkLab","bwa") = pfactreal("UnSkLab","bwa");
Swap qfactsup("UnSkLab","nam") = pfactreal("UnSkLab","nam");
Swap qfactsup("UnSkLab","zaf") = pfactreal("UnSkLab","zaf");
Swap qfactsup("UnSkLab","xsc") = pfactreal("UnSkLab","xsc");
!Swap qfactsup("UnSkLab","ZAF") = ps("UnSkLab","ZAF");

! FISCAL NEUTRALITY ASSUMPTIONS: endogenize consumption tax and fix the ratio 
! of tax revenue to net national income 
!Swap tp("ZAF") = del_ttaxr("ZAF") ;
!Swap tp("egy") = del_ttaxr("egy") ;
!Swap tp("RestofAfrica") = del_ttaxr("RestofAfrica") ;
!Swap tp("xnf") = del_ttaxr("xnf") ;
!Swap tp("xac") = del_ttaxr("xac") ;
!Swap tp("eth") = del_ttaxr("eth") ;
!Swap tp("ken") = del_ttaxr("ken") ;
!Swap tp("mdg") = del_ttaxr("mdg") ;
!Swap tp("mwi") = del_ttaxr("mwi") ;
!Swap tp("mus") = del_ttaxr("mus") ;
!Swap tp("moz") = del_ttaxr("moz") ;
!Swap tp("rwa") = del_ttaxr("rwa") ;
!Swap tp("tza") = del_ttaxr("tza") ;
!Swap tp("uga") = del_ttaxr("uga") ;
!Swap tp("zmb") = del_ttaxr("zmb") ;
!Swap tp("zwe") = del_ttaxr("zwe") ;
!Swap tp("xec") = del_ttaxr("xec") ;
!Swap tp("bwa") = del_ttaxr("bwa") ;
!Swap tp("nam") = del_ttaxr("nam") ;
!Swap tp("zaf") = del_ttaxr("zaf") ;
!Swap tp("xsc") = del_ttaxr("xsc") ;
!Swap dpgov("ZAF") = ug("ZAF");

! It DOES NOT MAKE SENSE to implement the unemployment closure without tax
! replacement. If you do so, you will get an illusory rise in employment as real
! wages automatically fall.