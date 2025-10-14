TITLE Ca R-type channel with medium threshold for activation

NEURON {
    SUFFIX glia__dbbs__Cav2_3__0
    THREADSAFE
    USEION ca READ eca WRITE ica
    RANGE gcabar, m, h, g, gmax
    RANGE inf_0, inf_1, tau_0, tau_1
}

UNITS {
    (mA) = (milliamp)
    (mV) = (millivolt)
}

PARAMETER {
    celsius
    gcabar = 0 (mho/cm2)
}

STATE {
    m
    h
}

ASSIGNED {
    inf_0
    inf_1
    tau_0 (ms)
    tau_1 (ms)
    g (mho/cm2)
    gmax (mho/cm2)
}

BREAKPOINT {
    SOLVE states METHOD cnexp
    g = gcabar*m*m*m*h
    ica = g*(v-eca)
    IF (g>gmax) {
        gmax = g
    }
}

INITIAL {
    mhn(v)
    m = inf_0
    h = inf_1
    g = gcabar*m*m*m*h
    ica = g*(v-eca)
    gmax = g
}

DERIVATIVE states {
    mhn(v)
    m' = (inf_0-m)/tau_0
    h' = (inf_1-h)/tau_1
}

FUNCTION varss(v(mV), i) {
    IF (i == 0) {
        varss = 1/(1+exp((v+48.5)/(-3)))
    } ELSE {
        varss = 1/(1+exp((v+53)/(1)))
    }
}

FUNCTION vartau(v(mV), i) (ms) {
    IF (i == 0) {
        vartau = 50
    } ELSE {
        vartau = 5
    }
}

PROCEDURE mhn(v(mV)) {
    tau_0 = vartau(v, 0)
    tau_1 = vartau(v, 1)
    inf_0 = varss(v, 0)
    inf_1 = varss(v, 1)
}
