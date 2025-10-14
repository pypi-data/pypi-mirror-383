COMMENT

The basic code of Example 9.8 and Example 9.9 from NEURON book was adapted as:

1) Extended using parameters from Schmidt et al. 2003.
2) Pump rate was tuned according to data from Maeda et al. 1999
3) DCM was introduced and tuned to approximate the effect of radial diffusion

Reference: Anwar H, Hong S, De Schutter E (2010) Controlling Ca2+-activated K+ channels with models of Ca2+ buffering in Purkinje cell. Cerebellum*

*Article available as Open Access

PubMed link: http://www.ncbi.nlm.nih.gov/pubmed/20981513

Written by Haroon Anwar, Computational Neuroscience Unit, Okinawa Institute of Science and Technology, 2010.
Contact: Haroon Anwar (anwar@oist.jp)

ENDCOMMENT

NEURON {
    SUFFIX glia__dbbs__cdp5__CAM
    USEION ca READ cao, ica WRITE cai
    RANGE Nannuli, Buffnull2, rf3, rf4, vrat
    RANGE CAM0, CAM1C, CAM2C, CAM1N2C, CAM1N, CAM2N, CAM2N1C, CAM1C1N, CAM4
    RANGE TotalPump
}

UNITS {
    (mol) = (1)
    (molar) = (1/liter)
    (mM) = (millimolar)
    (um) = (micron)
    (mA) = (milliamp)
}

CONSTANT {
    FARADAY = 9.6520
    PI = 3.14
    cao = 2 (mM)
}

PARAMETER {
    diam (um)
    Nannuli = 10.9495 (1)
    celsius (degC)
    cainull = 45e-6 (mM)
    mginull = .59 (mM)
    Buffnull1 = 0 (mM)
    rf1 = 0.0134329 (/ms mM)
    rf2 = 0.0397469 (/ms)
    Buffnull2 = 60.9091 (mM)
    rf3 = 0.1435 (/ms mM)
    rf4 = 0.0014 (/ms)
    BTCnull = 0 (mM)
    b1 = 5.33 (/ms mM)
    b2 = 0.08 (/ms)
    DMNPEnull = 0 (mM)
    c1 = 5.63 (/ms mM)
    c2 = 0.107e-3 (/ms)
    CBnull = .16 (mM)
    nf1 = 43.5 (/ms mM)
    nf2 = 3.58e-2 (/ms)
    ns1 = 5.5 (/ms mM)
    ns2 = 0.26e-2 (/ms)
    PVnull = .08 (mM)
    m1 = 1.07e2 (/ms mM)
    m2 = 9.5e-4 (/ms)
    p1 = 0.8 (/ms mM)
    p2 = 2.5e-2 (/ms)
    CAM_start = 0.03 (mM)
    Kd1C = 0.00965 (mM)
    K1Coff = 0.04 (/ms)
    K1Con = 5.4 (/mM ms)
    Kd2C = 0.00105 (mM)
    K2Coff = 0.00925 (/ms)
    K2Con = 15 (/mM ms)
    Kd1N = 0.0275 (uM)
    K1Noff = 2.5 (/ms)
    K1Non = 142.5 (/mM ms)
    Kd2N = 0.00615 (mM)
    K2Noff = 0.75 (/ms)
    K2Non = 175 (/mM ms)
    kpmp1 = 3e-3 (/mM/ms)
    kpmp2 = 1.75e-5 (/ms)
    kpmp3 = 7.255e-5 (/ms)
    TotalPump = 1e-9 (mol/cm2)
}

ASSIGNED {
    parea (um)
    parea2 (um)
    mgi (mM)
    vrat (1)
}

STATE {
    cai
    ca (mM)
    mg (mM)
    Buff1 (mM)
    Buff1_ca (mM)
    Buff2 (mM)
    Buff2_ca (mM)
    BTC (mM)
    BTC_ca (mM)
    DMNPE (mM)
    DMNPE_ca (mM)
    CB (mM)
    CB_f_ca (mM)
    CB_ca_s (mM)
    CB_ca_ca (mM)
    PV (mM)
    PV_ca (mM)
    PV_mg (mM)
    CAM0 (mM)
    CAM1C (mM)
    CAM2C (mM)
    CAM1N2C (mM)
    CAM1N (mM)
    CAM2N (mM)
    CAM2N1C (mM)
    CAM1C1N (mM)
    CAM4 (mM)
    pump (mol/cm2)
    pumpca (mol/cm2)
}

BREAKPOINT {
    SOLVE state METHOD sparse
    cai = ca
}

INITIAL {
    factors()
    ca = cainull
    mg = mginull
    Buff1 = ssBuff1()
    Buff1_ca = ssBuff1ca()
    Buff2 = ssBuff2()
    Buff2_ca = ssBuff2ca()
    BTC = ssBTC()
    BTC_ca = ssBTCca()
    DMNPE = ssDMNPE()
    DMNPE_ca = ssDMNPEca()
    CB = ssCB(kdf(), kds())
    CB_f_ca = ssCBfast(kdf(), kds())
    CB_ca_s = ssCBslow(kdf(), kds())
    CB_ca_ca = ssCBca(kdf(), kds())
    PV = ssPV(kdc(), kdm())
    PV_ca = ssPVca(kdc(), kdm())
    PV_mg = ssPVmg(kdc(), kdm())
    CAM0 = CAM_start
    CAM1C = 0
    CAM2C = 0
    CAM1N2C = 0
    CAM1N = 0
    CAM2N = 0
    CAM2N1C = 0
    CAM1C1N = 0
    CAM4 = 0
    parea = PI*diam
    parea2 = PI*(diam-0.2)
    ica = 0
    pump = TotalPump
    pumpca = 0
    cai = ca
}

PROCEDURE factors() {
    LOCAL r, dr2
    r = 1/2
    dr2 = r/(Nannuli-1)/2
    vrat = PI*(r-dr2/2)*2*dr2
    r = r-dr2
}

KINETIC state {
    LOCAL dsq, dsqvol
    COMPARTMENT diam*diam*vrat {ca mg Buff1 Buff1_ca Buff2 Buff2_ca BTC BTC_ca DMNPE DMNPE_ca CB CB_f_ca CB_ca_s CB_ca_ca PV PV_ca PV_mg}
    COMPARTMENT (1e10)*parea {pump pumpca}
    ~ ca+pump <-> pumpca (kpmp1*parea*(1e10), kpmp2*parea*(1e10))
    ~ pumpca <-> pump (kpmp3*parea*(1e10), 0)
    CONSERVE pump+pumpca = TotalPump*parea*(1e10)
    ~ ca << (-ica*PI*diam/(2*FARADAY))
    dsq = diam*diam
    dsqvol = dsq*vrat
    ~ ca+Buff1 <-> Buff1_ca (rf1*dsqvol, rf2*dsqvol)
    ~ ca+Buff2 <-> Buff2_ca (rf3*dsqvol, rf4*dsqvol)
    ~ ca+BTC <-> BTC_ca (b1*dsqvol, b2*dsqvol)
    ~ ca+DMNPE <-> DMNPE_ca (c1*dsqvol, c2*dsqvol)
    ~ ca+CB <-> CB_ca_s (nf1*dsqvol, nf2*dsqvol)
    ~ ca+CB <-> CB_f_ca (ns1*dsqvol, ns2*dsqvol)
    ~ ca+CB_f_ca <-> CB_ca_ca (nf1*dsqvol, nf2*dsqvol)
    ~ ca+CB_ca_s <-> CB_ca_ca (ns1*dsqvol, ns2*dsqvol)
    ~ ca+PV <-> PV_ca (m1*dsqvol, m2*dsqvol)
    ~ mg+PV <-> PV_mg (p1*dsqvol, p2*dsqvol)
    ~ ca+CAM0 <-> CAM1C (K1Con*dsqvol, K1Coff*dsqvol)
    ~ ca+CAM1C <-> CAM2C (K2Con*dsqvol, K2Coff*dsqvol)
    ~ ca+CAM2C <-> CAM1N2C (K1Non*dsqvol, K1Noff*dsqvol)
    ~ ca+CAM1N2C <-> CAM4 (K2Non*dsqvol, K2Noff*dsqvol)
    ~ ca+CAM0 <-> CAM1N (K1Non*dsqvol, K1Noff*dsqvol)
    ~ ca+CAM1N <-> CAM2N (K2Non*dsqvol, K2Noff*dsqvol)
    ~ ca+CAM2N <-> CAM2N1C (K1Con*dsqvol, K1Coff*dsqvol)
    ~ ca+CAM2N1C <-> CAM4 (K2Con*dsqvol, K2Coff*dsqvol)
    ~ ca+CAM1C <-> CAM1C1N (K1Non*dsqvol, K1Noff*dsqvol)
    ~ ca+CAM1N <-> CAM1C1N (K1Con*dsqvol, K1Coff*dsqvol)
    ~ ca+CAM1C1N <-> CAM1N2C (K2Con*dsqvol, K2Coff*dsqvol)
    ~ ca+CAM1C1N <-> CAM2N1C (K2Non*dsqvol, K2Noff*dsqvol)
    mgi = mg
}

FUNCTION ssBuff1() (mM) {
    ssBuff1 = Buffnull1/(1+((rf1/rf2)*cainull))
}

FUNCTION ssBuff1ca() (mM) {
    ssBuff1ca = Buffnull1/(1+(rf2/(rf1*cainull)))
}

FUNCTION ssBuff2() (mM) {
    ssBuff2 = Buffnull2/(1+((rf3/rf4)*cainull))
}

FUNCTION ssBuff2ca() (mM) {
    ssBuff2ca = Buffnull2/(1+(rf4/(rf3*cainull)))
}

FUNCTION ssBTC() (mM) {
    ssBTC = BTCnull/(1+((b1/b2)*cainull))
}

FUNCTION ssBTCca() (mM) {
    ssBTCca = BTCnull/(1+(b2/(b1*cainull)))
}

FUNCTION ssDMNPE() (mM) {
    ssDMNPE = DMNPEnull/(1+((c1/c2)*cainull))
}

FUNCTION ssDMNPEca() (mM) {
    ssDMNPEca = DMNPEnull/(1+(c2/(c1*cainull)))
}

FUNCTION ssCB(kdf_0, kds_0) (mM) {
    ssCB = CBnull/(1+kdf_0+kds_0+(kdf_0*kds_0))
}

FUNCTION ssCBfast(kdf_0, kds_0) (mM) {
    ssCBfast = (CBnull*kds_0)/(1+kdf_0+kds_0+(kdf_0*kds_0))
}

FUNCTION ssCBslow(kdf_0, kds_0) (mM) {
    ssCBslow = (CBnull*kdf_0)/(1+kdf_0+kds_0+(kdf_0*kds_0))
}

FUNCTION ssCBca(kdf_0, kds_0) (mM) {
    ssCBca = (CBnull*kdf_0*kds_0)/(1+kdf_0+kds_0+(kdf_0*kds_0))
}

FUNCTION kdf() (1) {
    kdf = (cainull*nf1)/nf2
}

FUNCTION kds() (1) {
    kds = (cainull*ns1)/ns2
}

FUNCTION kdc() (1) {
    kdc = (cainull*m1)/m2
}

FUNCTION kdm() (1) {
    kdm = (mginull*p1)/p2
}

FUNCTION ssPV(kdc_0, kdm_0) (mM) {
    ssPV = PVnull/(1+kdc_0+kdm_0)
}

FUNCTION ssPVca(kdc_0, kdm_0) (mM) {
    ssPVca = (PVnull*kdc_0)/(1+kdc_0+kdm_0)
}

FUNCTION ssPVmg(kdc_0, kdm_0) (mM) {
    ssPVmg = (PVnull*kdm_0)/(1+kdc_0+kdm_0)
}
