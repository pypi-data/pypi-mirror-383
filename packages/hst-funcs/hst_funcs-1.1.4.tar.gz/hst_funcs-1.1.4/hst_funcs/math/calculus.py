def CURL(v,x):
    from sympy import diff
    import sympy as sp
    out0=diff(v[2],x[1])-diff(v[1],x[2])
    out1=diff(v[0],x[2])-diff(v[2],x[0])
    out2=diff(v[1],x[0])-diff(v[0],x[1])
    return sp.Matrix([out0,out1,out2])

def GRAD(v,x):
    from sympy import diff,Matrix,zeros
    n=len(v)
    out=zeros(n,1)
    for i in range(n):
        out[i]=diff(v[i],x[i])
    return out

def LAPLACIAN(v,x):
    from sympy import diff
    import sympy as sp
    N=len(x)
    out=0
    for i in range(N):
        out += diff(diff(v[i],x[i]),x[i])
    return out

def DIV(v,x):
    from sympy import diff
    N=len(x)
    out=0
    for i in range(N):
        out += diff(v[i],x[i])
    return out

def JACOBI(v,x):
    from sympy import Matrix,diff
    n=len(v)
    J=zeros(n)
    for n_i in range(n):
        for n_j in range(n):
            J[n_i,n_j]=diff(v[n_i],x[n_j])
    J=Matrix(J)
    return J.det().simplify()

# symbolic vandermonde matrix
def vander(w,n):
        from sympy import zeros
        out=zeros(n)
        for i in range(n):
            for j in range(n):
                out[i,j]=w**(i*j)
        return out

# numeric vandermonde matrix
def vander_numeric(w,n):
        import numpy as np
        out=np.zeros([n,n],dtype='complex_')
        for k in range(n):
            for kk in range(n):
                out[k,kk]=w**(k*kk)
        return out
