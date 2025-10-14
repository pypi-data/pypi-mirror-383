NEURON {
    POINT_PROCESS glia__dbbs__NMDA__granule
    NONSPECIFIC_CURRENT i
    RANGE Q10_diff, Q10_channel
    RANGE g, ic
    RANGE Cdur, Erev, T, Tmax
    RANGE Rb, Ru, Rd, Rr, Ro, Rc, rb, gmax, RdRate
    RANGE tau_1, tau_rec, tau_facil, U, u0
    RANGE PRE
    RANGE Used
    RANGE MgBlock, v0_block, k_block
    RANGE diffuse, Trelease, lamd, Diff, M, Rd, nd, syntype, gmax_factor
}

UNITS {
    (nA) = (nanoamp)
    (mV) = (millivolt)
    (umho) = (micromho)
    (mM) = (milli/liter)
    (pS) = (picosiemens)
    (nS) = (nanosiemens)
    (um) = (micrometer)
    PI = (pi) (1)
}

PARAMETER {
    syntype
    gmax_factor = 1
    gmax = 18800 (pS)
    Q10_diff = 1.5
    Q10_channel = 2.4
    U = 0.42 (1) <0,1>
    tau_rec = 8 (ms) <1e-9,1e9>
    tau_facil = 5 (ms) <0,1e9>
    M = 21.515
    Rd = 1.03 (um)
    Diff = 0.223 (um2/ms)
    tau_1 = 1 (ms) <1e-9,1e9>
    u0 = 0 (1) <0,1>
    Tmax = 1 (mM)
    Cdur = 0.3 (ms)
    Rb = 5 (/ms/mM)
    Ru = 0.1 (/ms)
    RdRate = 12e-3 (/ms)
    Rr = 9e-3 (/ms)
    Ro = 3e-2 (/ms)
    Rc = 0.966 (/ms)
    Erev = -3.7 (mV)
    v0_block = -20 (mV)
    k_block = 13 (mV)
    nd = 1
    kB = 0.44 (mM)
    diffuse = 1
    lamd = 20 (nm)
    celsius (degC)
}

ASSIGNED {
    v (mV)
    i (nA)
    ic (nA)
    g (pS)
    rb (/ms)
    T (mM)
    x
    Trelease (mM)
    tspike[100] (ms)
    PRE[100]
    Mres (mM)
    MgBlock
    numpulses
    tzero
    gbar_Q10 (mho/cm2)
    Q10 (1)
}

STATE {
    C0
    C1
    C2
    D
    O
}

INITIAL {
    rates(v)
    C0 = 1
    C1 = 0
    C2 = 0
    D = 0
    O = 0
    T = 0
    numpulses = 0
    gbar_Q10 = Q10_diff^((celsius-30)/10)
    Q10 = Q10_channel^((celsius-30)/10)
    Mres = 1e3*(1e3*1e15/6.022e23*M)
    FROM i = 1 TO 100 {
        PRE[i-1] = 0
        tspike[i-1] = 0
    }
    tspike[0] = 1e12(ms)
    IF (tau_1>=tau_rec) {
        printf("Warning: tau_1 (%g) should never be higher neither equal to tau_rec (%g)!\n", tau_1, tau_rec)
        tau_rec = tau_1+1e-5
    }
}

FUNCTION imax(a, b) {
    IF (a>b) {
        imax = a
    } ELSE {
        imax = b
    }
}

FUNCTION diffusione() {
    LOCAL DifWave, i, cntc, fi, aaa
    DifWave = 0
    cntc = imax(numpulses-100, 0)
    FROM i = cntc TO numpulses {
        fi = fmod(i, 100)
        tzero = tspike[fi]
        IF (t>tzero) {
            aaa = (-Rd*Rd/(4*Diff*(t-tzero)))
            IF (fabs(aaa)<699) {
                DifWave = DifWave+PRE[fi]*Mres*exp(aaa)/((4*PI*Diff*(1e-3)*lamd)*(t-tzero))
            } ELSE {
                IF (aaa>0) {
                    DifWave = DifWave+PRE[fi]*Mres*exp(699)/((4*PI*Diff*(1e-3)*lamd)*(t-tzero))
                } ELSE {
                    DifWave = DifWave+PRE[fi]*Mres*exp(-699)/((4*PI*Diff*(1e-3)*lamd)*(t-tzero))
                }
            }
        }
    }
    diffusione = DifWave
}

BREAKPOINT {
    rates(v)
    SOLVE kstates METHOD sparse
    g = gmax*gbar_Q10*O*gmax_factor
    i = (1e-6)*g*(v-Erev)*MgBlock
    ic = i
}

KINETIC kstates {
    Trelease = diffusione()
    rb = Rb*Trelease
    ~ C0 <-> C1 (rb*Q10, Ru*Q10)
    ~ C1 <-> C2 (rb*Q10, Ru*Q10)
    ~ C2 <-> D (RdRate*Q10, Rr*Q10)
    ~ C2 <-> O (Ro*Q10, Rc*Q10)
    CONSERVE C0+C1+C2+D+O = 1
}

PROCEDURE rates(v(mV)) {
    TABLE MgBlock DEPEND v0_block,k_block FROM -120 TO 30 WITH 150
    MgBlock = 1/(1+exp(-(v-v0_block)/k_block))
}

NET_RECEIVE (weight, on, nspike, tzero(ms), y, z, u, tsyn(ms)) {
    LOCAL fi
    INITIAL {
        y = 0
        z = 0
        u = u0
        tsyn = t
        nspike = 1
    }
    IF (flag == 0) {
        nspike = nspike+1
        IF (!on) {
            tzero = t
            on = 1
            z = z*exp(-(t-tsyn)/(tau_rec))
            z = z+(y*(exp(-(t-tsyn)/tau_1)-exp(-(t-tsyn)/(tau_rec)))/((tau_1/(tau_rec))-1))
            y = y*exp(-(t-tsyn)/tau_1)
            x = 1-y-z
            IF (tau_facil>0) {
                u = u*exp(-(t-tsyn)/tau_facil)
                u = u+U*(1-u)
            } ELSE {
                u = U
            }
            y = y+x*u
            T = Tmax*y
            fi = fmod(numpulses, 100)
            PRE[fi] = y
            tspike[fi] = t
            numpulses = numpulses+1
            tsyn = t
        }
        net_send(Cdur, nspike)
    }
    IF (flag == nspike) {
        tzero = t
        T = 0
        on = 0
    }
}
