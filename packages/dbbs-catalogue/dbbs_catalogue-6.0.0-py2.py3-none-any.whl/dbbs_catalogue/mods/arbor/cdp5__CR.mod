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

Modified by Stefano Masoli, Department Brain and Behavioral Sciences, University of Pavia, 2015

1) Buffer for Granule cell model 2015, without Parvalbumin and Calretinin instead of Calbindin.

ENDCOMMENT

NEURON {
    SUFFIX glia__dbbs__cdp5__CR
    USEION ca READ cao, ica WRITE cai
    RANGE Nannuli, Buffnull2, rf3, rf4, vrat, cainull, CR, CR_1C_0N, CR_2C_2N, CR_1V, CRnull
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
    CRnull = 0.9 (mM)
    nT1 = 1.8 (/ms mM)
    nT2 = 0.053 (/ms)
    nR1 = 310 (/ms mM)
    nR2 = 0.02 (/ms)
    nV1 = 7.3 (/ms mM)
    nV2 = 0.24 (/ms)
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
    CR (mM)
    CR_1C_0N (mM)
    CR_2C_0N (mM)
    CR_2C_1N (mM)
    CR_1C_1N (mM)
    CR_0C_1N (mM)
    CR_0C_2N (mM)
    CR_1C_2N (mM)
    CR_2C_2N (mM)
    CR_1V (mM)
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
    CR = CRnull
    CR_1C_0N = 0
    CR_2C_0N = 0
    CR_2C_1N = 0
    CR_1C_1N = 0
    CR_0C_1N = 0
    CR_0C_2N = 0
    CR_1C_2N = 0
    CR_2C_2N = 0
    CR_1V = 0
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
    COMPARTMENT diam*diam*vrat {ca Buff1 Buff1_ca Buff2 Buff2_ca BTC BTC_ca DMNPE DMNPE_ca CR CR_1C_0N CR_2C_0N CR_2C_1N CR_0C_1N CR_0C_2N CR_1C_2N CR_1C_1N CR_2C_1N CR_1C_2N CR_2C_2N}
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
    ~ ca+CR <-> CR_1C_0N (nT1*dsqvol, nT2*dsqvol)
    ~ ca+CR_1C_0N <-> CR_2C_0N (nR1*dsqvol, nR2*dsqvol)
    ~ ca+CR_2C_0N <-> CR_2C_1N (nT1*dsqvol, nT2*dsqvol)
    ~ ca+CR <-> CR_0C_1N (nT1*dsqvol, nT2*dsqvol)
    ~ ca+CR_0C_1N <-> CR_0C_2N (nR1*dsqvol, nR2*dsqvol)
    ~ ca+CR_0C_2N <-> CR_1C_2N (nT1*dsqvol, nT2*dsqvol)
    ~ ca+CR_2C_1N <-> CR_2C_2N (nR1*dsqvol, nR2*dsqvol)
    ~ ca+CR_1C_2N <-> CR_2C_2N (nR1*dsqvol, nR2*dsqvol)
    ~ ca+CR_1C_0N <-> CR_1C_1N (nT1*dsqvol, nT2*dsqvol)
    ~ ca+CR_0C_1N <-> CR_1C_1N (nT1*dsqvol, nT2*dsqvol)
    ~ ca+CR_1C_1N <-> CR_2C_1N (nR1*dsqvol, nR2*dsqvol)
    ~ ca+CR_1C_1N <-> CR_1C_2N (nR1*dsqvol, nR2*dsqvol)
    ~ ca+CR <-> CR_1V (nV1*dsqvol, nV2*dsqvol)
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
