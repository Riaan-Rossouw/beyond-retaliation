! ---------------------------------------------------------------------------
! POL3F -- Scenario 5 (policy response + DSM export realisation)
! "Beyond Retaliation: How South Africa Can Effectively Counter the USA's
!  Tariff Wars".  GDyn v3.6, GTAP 11 (2017), 16 sectors x 7 regions.
!
! POL2 plus 46 ams<->qxs swaps.  Applied from 2026; 2025 uses POL2.
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

! 4. DSM EXPORT OPPORTUNITY REALISATION (ZAF)
! Bilateral export volumes into the five non-USA destinations are set
! exogenously to the DSM-identified potential; ams becomes the endogenous
! residual reporting the market-access improvement required to deliver them.
! Coal and Mining are excluded: Section 4.6.3 excludes mining and energy
! products from the DSM scope.  Four flows below US$50m are excluded on
! materiality (LiveMeat->GBR, TexApp->GBR, TradeTran->SACUSADC, Auto->CHN).
! ZAF->USA is excluded by assumption.
! Swap ams("Auto","ZAF","CHN") = qxs("Auto","ZAF","CHN");   ! EXCLUDED
Swap ams("ChemPlast","ZAF","CHN") = qxs("ChemPlast","ZAF","CHN");
! Swap ams("Coal","ZAF","CHN") = qxs("Coal","ZAF","CHN");   ! EXCLUDED
Swap ams("GrainCrop","ZAF","CHN") = qxs("GrainCrop","ZAF","CHN");
Swap ams("LiveMeat","ZAF","CHN") = qxs("LiveMeat","ZAF","CHN");
Swap ams("MachEquip","ZAF","CHN") = qxs("MachEquip","ZAF","CHN");
Swap ams("Metals","ZAF","CHN") = qxs("Metals","ZAF","CHN");
! Swap ams("Mining","ZAF","CHN") = qxs("Mining","ZAF","CHN");   ! EXCLUDED
Swap ams("OthAgFood","ZAF","CHN") = qxs("OthAgFood","ZAF","CHN");
Swap ams("OthManuf","ZAF","CHN") = qxs("OthManuf","ZAF","CHN");
Swap ams("TexApp","ZAF","CHN") = qxs("TexApp","ZAF","CHN");
Swap ams("TradeTran","ZAF","CHN") = qxs("TradeTran","ZAF","CHN");
Swap ams("Auto","ZAF","EU27") = qxs("Auto","ZAF","EU27");
Swap ams("ChemPlast","ZAF","EU27") = qxs("ChemPlast","ZAF","EU27");
! Swap ams("Coal","ZAF","EU27") = qxs("Coal","ZAF","EU27");   ! EXCLUDED
Swap ams("GrainCrop","ZAF","EU27") = qxs("GrainCrop","ZAF","EU27");
Swap ams("LiveMeat","ZAF","EU27") = qxs("LiveMeat","ZAF","EU27");
Swap ams("MachEquip","ZAF","EU27") = qxs("MachEquip","ZAF","EU27");
Swap ams("Metals","ZAF","EU27") = qxs("Metals","ZAF","EU27");
! Swap ams("Mining","ZAF","EU27") = qxs("Mining","ZAF","EU27");   ! EXCLUDED
Swap ams("OthAgFood","ZAF","EU27") = qxs("OthAgFood","ZAF","EU27");
Swap ams("OthManuf","ZAF","EU27") = qxs("OthManuf","ZAF","EU27");
Swap ams("TexApp","ZAF","EU27") = qxs("TexApp","ZAF","EU27");
Swap ams("TradeTran","ZAF","EU27") = qxs("TradeTran","ZAF","EU27");
Swap ams("Auto","ZAF","GBR") = qxs("Auto","ZAF","GBR");
Swap ams("ChemPlast","ZAF","GBR") = qxs("ChemPlast","ZAF","GBR");
! Swap ams("Coal","ZAF","GBR") = qxs("Coal","ZAF","GBR");   ! EXCLUDED
Swap ams("GrainCrop","ZAF","GBR") = qxs("GrainCrop","ZAF","GBR");
! Swap ams("LiveMeat","ZAF","GBR") = qxs("LiveMeat","ZAF","GBR");   ! EXCLUDED
Swap ams("MachEquip","ZAF","GBR") = qxs("MachEquip","ZAF","GBR");
Swap ams("Metals","ZAF","GBR") = qxs("Metals","ZAF","GBR");
! Swap ams("Mining","ZAF","GBR") = qxs("Mining","ZAF","GBR");   ! EXCLUDED
Swap ams("OthAgFood","ZAF","GBR") = qxs("OthAgFood","ZAF","GBR");
Swap ams("OthManuf","ZAF","GBR") = qxs("OthManuf","ZAF","GBR");
! Swap ams("TexApp","ZAF","GBR") = qxs("TexApp","ZAF","GBR");   ! EXCLUDED
Swap ams("TradeTran","ZAF","GBR") = qxs("TradeTran","ZAF","GBR");
Swap ams("Auto","ZAF","ROW") = qxs("Auto","ZAF","ROW");
Swap ams("ChemPlast","ZAF","ROW") = qxs("ChemPlast","ZAF","ROW");
! Swap ams("Coal","ZAF","ROW") = qxs("Coal","ZAF","ROW");   ! EXCLUDED
Swap ams("GrainCrop","ZAF","ROW") = qxs("GrainCrop","ZAF","ROW");
Swap ams("LiveMeat","ZAF","ROW") = qxs("LiveMeat","ZAF","ROW");
Swap ams("MachEquip","ZAF","ROW") = qxs("MachEquip","ZAF","ROW");
Swap ams("Metals","ZAF","ROW") = qxs("Metals","ZAF","ROW");
! Swap ams("Mining","ZAF","ROW") = qxs("Mining","ZAF","ROW");   ! EXCLUDED
Swap ams("OthAgFood","ZAF","ROW") = qxs("OthAgFood","ZAF","ROW");
Swap ams("OthManuf","ZAF","ROW") = qxs("OthManuf","ZAF","ROW");
Swap ams("TexApp","ZAF","ROW") = qxs("TexApp","ZAF","ROW");
Swap ams("TradeTran","ZAF","ROW") = qxs("TradeTran","ZAF","ROW");
Swap ams("Auto","ZAF","SACUSADC") = qxs("Auto","ZAF","SACUSADC");
Swap ams("ChemPlast","ZAF","SACUSADC") = qxs("ChemPlast","ZAF","SACUSADC");
! Swap ams("Coal","ZAF","SACUSADC") = qxs("Coal","ZAF","SACUSADC");   ! EXCLUDED
Swap ams("GrainCrop","ZAF","SACUSADC") = qxs("GrainCrop","ZAF","SACUSADC");
Swap ams("LiveMeat","ZAF","SACUSADC") = qxs("LiveMeat","ZAF","SACUSADC");
Swap ams("MachEquip","ZAF","SACUSADC") = qxs("MachEquip","ZAF","SACUSADC");
Swap ams("Metals","ZAF","SACUSADC") = qxs("Metals","ZAF","SACUSADC");
! Swap ams("Mining","ZAF","SACUSADC") = qxs("Mining","ZAF","SACUSADC");   ! EXCLUDED
Swap ams("OthAgFood","ZAF","SACUSADC") = qxs("OthAgFood","ZAF","SACUSADC");
Swap ams("OthManuf","ZAF","SACUSADC") = qxs("OthManuf","ZAF","SACUSADC");
Swap ams("TexApp","ZAF","SACUSADC") = qxs("TexApp","ZAF","SACUSADC");
! Swap ams("TradeTran","ZAF","SACUSADC") = qxs("TradeTran","ZAF","SACUSADC");   ! EXCLUDED
