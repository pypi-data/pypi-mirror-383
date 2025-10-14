NEURON {
    SUFFIX glia__dbbs__Kv3_4__0
    USEION k READ ek WRITE ik
    RANGE gkbar, ik
    RANGE minf, hinf, mtau, htau
}

UNITS {
    (mV) = (millivolt)
    (mA) = (milliamp)
}

CONSTANT {
    q10 = 3
}

PARAMETER {
    celsius (degC)
    v (mV)
    gkbar = .004 (mho/cm2)
    mivh = -24 (mV)
    mik = 15.4 (1)
    mty0 = .00012851
    mtvh1 = 100.7 (mV)
    mtk1 = 12.9 (1)
    mtvh2 = -56.0 (mV)
    mtk2 = -23.1 (1)
    hiy0 = .31
    hiA = .69
    hivh = -5.802 (mV)
    hik = 11.2 (1)
}

ASSIGNED {
    minf
    mtau (ms)
    hinf
    htau (ms)
    qt
}

STATE {
    m
    h
}

INITIAL {
    rates(v)
    m = minf
    h = hinf
    qt = q10^((celsius-37)/10)
}

BREAKPOINT {
    SOLVE states METHOD cnexp
    ik = gkbar*m^3*h*(v-ek)
}

DERIVATIVE states {
    rates(v)
    m' = (minf-m)/mtau
    h' = (hinf-h)/htau
}

PROCEDURE rates(Vm(mV)) {
    LOCAL v_
    v_ = Vm+11
    minf = 1/(1+exp(-(v_-mivh)/mik))
    mtau = (1000)*mtau_func(v_)/qt
    hinf = hiy0+hiA/(1+exp((v_-hivh)/hik))
    htau = 1000*htau_func(v_)/qt
}

FUNCTION mtau_func(v(mV)) (ms) {
    IF (v<-35) {
        mtau_func = (3.4225e-5+.00498*exp(-v/-28.29))*3
    } ELSE {
        mtau_func = (mty0+1/(exp((v+mtvh1)/mtk1)+exp((v+mtvh2)/mtk2)))
    }
}

FUNCTION htau_func(Vm(mV)) (ms) {
    IF (Vm>0) {
        htau_func = .0012+.0023*exp(-.141*Vm)
    } ELSE {
        htau_func = 1.2202e-05+.012*exp(-((Vm-(-56.3))/49.6)^2)
    }
}
