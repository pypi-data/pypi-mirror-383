TITLE Ca R-type channel with medium threshold for activation

NEURON {
    SUFFIX glia__dbbs__Cav2_3__0
    THREADSAFE
    USEION ca READ eca WRITE ica
    RANGE gcabar, m, h, g, gmax
    RANGE inf, tau
}

UNITS {
    (mA) = (milliamp)
    (mV) = (millivolt)
}

PARAMETER {
    v (mV)
    celsius
    gcabar = 0 (mho/cm2)
}

STATE {
    m
    h
}

ASSIGNED {
    eca
    ica (mA/cm2)
    inf[2]
    tau[2] (ms)
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
    m = inf[0]
    h = inf[1]
    g = gcabar*m*m*m*h
    ica = g*(v-eca)
    gmax = g
}

DERIVATIVE states {
    mhn(v)
    m' = (inf[0]-m)/tau[0]
    h' = (inf[1]-h)/tau[1]
}

FUNCTION varss(v(mV), i) {
    IF (i == 0) {
        varss = 1/(1+exp((v+48.5(mV))/(-3(mV))))
    } ELSE IF (i == 1) {
        varss = 1/(1+exp((v+53(mV))/(1(mV))))
    }
}

FUNCTION vartau(v(mV), i) (ms) {
    IF (i == 0) {
        vartau = 50
    } ELSE IF (i == 1) {
        vartau = 5
    }
}

PROCEDURE mhn(v(mV)) {
    TABLE inf,tau DEPEND celsius FROM -100 TO 100 WITH 200
    FROM i = 0 TO 1 {
        tau[i] = vartau(v, i)
        inf[i] = varss(v, i)
    }
}
