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

Swap qgdp = afereg ;
!Swap DKHAT = SDKHAT ;
!Swap sqcgdsreg = SDRORT ;
Swap sqcgdsreg = srorge ;
Swap SDRORTW = sqcgdsworld ;
!Swap wqht = swqht ;