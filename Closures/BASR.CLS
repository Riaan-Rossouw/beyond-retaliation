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

! FIXED WAGE CLOSURE: endogenise unskilled labour endowment and fix real wage
!Swap qfactsup("UnSkLab","ZAF") = pfactreal("UnSkLab","ZAF");

! FISCAL NEUTRALITY ASSUMPTIONS: endogenize consumption tax and fix the ratio 
! of tax revenue to net national income 
!Swap tp = del_ttaxr ;

! It DOES NOT MAKE SENSE to implement the unemployment closure without tax
! replacement. If you do so, you will get an illusory rise in employment as real
! wages automatically fall.