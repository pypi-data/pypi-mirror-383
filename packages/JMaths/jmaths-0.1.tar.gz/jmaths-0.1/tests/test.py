if __name__ == '__main__':
    import JMaths as jm

    jv = jm.variable
    jf = jm.function
    je = jm.export

    x = jv.variable('x')

    f_x = jf.function(x)
    f_x.set_equations("x**2")
    f_x.delta = .3
    f_x.calculate([-3, 3])

    print(f"Domain: \n{f_x.domain}")
    print(f"Range: \n{f_x.range}")

    je.excelExport(f_x.domain, f_x.range, "Test2")



