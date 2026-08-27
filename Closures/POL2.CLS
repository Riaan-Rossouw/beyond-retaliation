! ---------------------------------------------------------------------------
! POL2 -- Scenarios 2 and 4 (South African policy response)
! "Beyond Retaliation: How South Africa Can Effectively Counter the USA's
!  Tariff Wars".  GDyn v3.6, GTAP 11 (2017), 16 sectors x 7 regions.
!
! Trade-balance mechanism for the real depreciation.
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

! 3. REAL EXCHANGE RATE VIA THE TRADE BALANCE (ZAF)
! The trade balance to income ratio is made exogenous and shocked; the
! regional savings distribution parameter becomes the endogenous residual.
! Forcing an improvement in the trade balance requires expenditure
! switching, which the model delivers as a real depreciation.  The
! depreciation is therefore an OUTCOME of the experiment, not an imposed
! price.
!
! This replaces the earlier  Swap incomeslack("ZAF") = pfactor("ZAF").
! That device hit the pfactor target by letting the regional income
! equation fail to balance.  Because EV is computed from regional income,
! it contaminated the welfare results.  The swap below keeps the regional
! accounts closed.
!
! DTBALR is an ORDINARY CHANGE variable: the shock is in percentage points
! of the trade-balance-to-income ratio, not a percentage change.
Swap dpsave("ZAF") = DTBALR("ZAF");
