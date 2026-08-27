! ---------------------------------------------------------------------------
! POL1 -- Scenarios 1 and 3 (South Africa passive)
! "Beyond Retaliation: How South Africa Can Effectively Counter the USA's
!  Tariff Wars".  GDyn v3.6, GTAP 11 (2017), 16 sectors x 7 regions.
!
! No South African policy response.  UNCHANGED from v3 - Scenarios 1 and 3 do not need re-running.
! ---------------------------------------------------------------------------

Exogenous
    af
    afe(ENDWC_COMM,PROD_COMM,REG) 
    afereg
    afesec
    ams
    ao
    atall 
    atm 
    atf 
    ats 
    atd 
    au
    avadiff
    avareg
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

Rest Endogenous;

! 1. NEO-KEYNESIAN UNSKILLED LABOUR MARKET (ZAF)
! The supply price of unskilled labour is fixed and the employed quantity
! becomes endogenous.
Swap qfactsup("UnSkLab","ZAF") = ps("UnSkLab","ZAF");

! 2. FISCAL NEUTRALITY (ZAF)
! Private consumption tax endogenous; the ratio of tax revenue to net
! national income held on its baseline path.  Required alongside the
! fixed-wage closure: without revenue replacement the unemployment closure
! produces an illusory employment gain.
Swap tp("ZAF") = del_ttaxr("ZAF");
