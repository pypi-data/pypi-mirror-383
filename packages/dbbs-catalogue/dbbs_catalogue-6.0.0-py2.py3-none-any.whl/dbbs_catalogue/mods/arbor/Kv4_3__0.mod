TITLE Cerebellum Granule Cell Model

COMMENT
        KA channel

	Author: E.D'Angelo, T.Nieus, A. Fontana
	Last revised: Egidio 3.12.2003

:Suffix from GRC_KA to Kv4_3
ENDCOMMENT

NEURON {
    SUFFIX glia__dbbs__Kv4_3__0
    USEION k READ ek WRITE ik
    RANGE gkbar, ik, g, alpha_a, beta_a, alpha_b, beta_b
    RANGE Aalpha_a, Kalpha_a, V0alpha_a
    RANGE Abeta_a, Kbeta_a, V0beta_a
    RANGE Aalpha_b, Kalpha_b, V0alpha_b
    RANGE Abeta_b, Kbeta_b, V0beta_b
    RANGE V0_ainf, K_ainf, V0_binf, K_binf
    RANGE a_inf, tau_a, b_inf, tau_b
}

UNITS {
    (mA) = (milliamp)
    (mV) = (millivolt)
}

PARAMETER {
    Aalpha_a = 0.8147 (/ms)
    Kalpha_a = -23.32708 (mV)
    V0alpha_a = -9.17203 (mV)
    Abeta_a = 0.1655 (/ms)
    Kbeta_a = 19.47175 (mV)
    V0beta_a = -18.27914 (mV)
    Aalpha_b = 0.0368 (/ms)
    Kalpha_b = 12.8433 (mV)
    V0alpha_b = -111.33209 (mV)
    Abeta_b = 0.0345 (/ms)
    Kbeta_b = -8.90123 (mV)
    V0beta_b = -49.9537 (mV)
    V0_ainf = -38 (mV)
    K_ainf = -17 (mV)
    V0_binf = -78.8 (mV)
    K_binf = 8.4 (mV)
    v (mV)
    gkbar = 0.0032 (mho/cm2)
    celsius
}

STATE {
    a
    b
}

ASSIGNED {
    a_inf
    b_inf
    tau_a (ms)
    tau_b (ms)
    g (mho/cm2)
    alpha_a (/ms)
    beta_a (/ms)
    alpha_b (/ms)
    beta_b (/ms)
}

INITIAL {
    rate(v, celsius)
    a = a_inf
    b = b_inf
}

BREAKPOINT {
    SOLVE states METHOD cnexp
    g = gkbar*a*a*a*b
    ik = g*(v-ek)
    alpha_a = alp_a(v, celsius)
    beta_a = bet_a(v, celsius)
    alpha_b = alp_b(v, celsius)
    beta_b = bet_b(v, celsius)
}

DERIVATIVE states {
    rate(v, celsius)
    a' = (a_inf-a)/tau_a
    b' = (b_inf-b)/tau_b
}

FUNCTION alp_a(v(mV), celsius) (/ms) {
    LOCAL Q10
    Q10 = 3^((celsius-25.5)/10)
    alp_a = Q10*Aalpha_a*sigm(v-V0alpha_a, Kalpha_a)
}

FUNCTION bet_a(v(mV), celsius) (/ms) {
    LOCAL Q10
    Q10 = 3^((celsius-25.5)/10)
    bet_a = Q10*Abeta_a/(exp((v-V0beta_a)/Kbeta_a))
}

FUNCTION alp_b(v(mV), celsius) (/ms) {
    LOCAL Q10
    Q10 = 3^((celsius-25.5)/10)
    alp_b = Q10*Aalpha_b*sigm(v-V0alpha_b, Kalpha_b)
}

FUNCTION bet_b(v(mV), celsius) (/ms) {
    LOCAL Q10
    Q10 = 3^((celsius-25.5)/10)
    bet_b = Q10*Abeta_b*sigm(v-V0beta_b, Kbeta_b)
}

PROCEDURE rate(v(mV), celsius) {
    LOCAL a_a, b_a, a_b, b_b
    a_a = alp_a(v, celsius)
    b_a = bet_a(v, celsius)
    a_b = alp_b(v, celsius)
    b_b = bet_b(v, celsius)
    a_inf = 1/(1+exp((v-V0_ainf)/K_ainf))
    tau_a = 1/(a_a+b_a)
    b_inf = 1/(1+exp((v-V0_binf)/K_binf))
    tau_b = 1/(a_b+b_b)
}

FUNCTION linoid(x(mV), y(mV)) (mV) {
    IF (fabs(x/y)<1e-6) {
        linoid = y*(1-x/y/2)
    } ELSE {
        linoid = x/(exp(x/y)-1)
    }
}

FUNCTION sigm(x(mV), y(mV)) {
    sigm = 1/(exp(x/y)+1)
}
