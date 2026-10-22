namespace Serena.Zyql {
    operation DjTrivalente(case : String) : Result[] {
        use q = Qubit[3];
        X(q[2]); H(q[2]); H(q[0]); H(q[1]);
        if case == "const-1" { X(q[2]); }
        elif case == "balanced" { CNOT(q[0], q[2]); CNOT(q[1], q[2]); }
        H(q[0]); H(q[1]);
        let r = [M(q[0]), M(q[1])];
        ResetAll(q);
        return r;
    }
}
