import pydantic
import typing


class RuntimeOptions(pydantic.BaseModel, validate_assignment=True, extra="forbid"):
    """C Runtime Simulation Flags

    https://openmodelica.org/doc/OpenModelicaUsersGuide/latest/simulationflags.html

    The relevant OM flag is shown in '[]' alongside parameter descriptions.

    Attributes
    ----------

    abortSlowSimulation : bool, optional
        Aborts if the simulation chatters (default False).

    alarm : int, optional
        Aborts after the given number of seconds (default=0 disables the alarm).

    clock : Literal["RT", "CYC", "CPU"] | None, optional
        Selects the type of clock to use. Valid options includes:
            RT    (monotonic real-time clock)
            CYC   (cpu cycles measured with RDTSC)
            CPU   (process-based CPU-time)

    cpu : bool, optional
        Dumps the cpu-time into the result file using the variable named $cpuTime (default False).

    csvOstep : str | None, optional
        Specifies csv-files for debug values for optimizer step (default None).

    cvodeNonlinearSolverIteration : CV_ITER | None, optional
        Nonlinear solver iteration for CVODE solver.
        Default depends on option cvode_linear_multistep_method. Valid values:
            CV_ITER.NEWTON - Newton iteration.
                Advised to use together with argument cvode_linear_multistep_method=CV.BDF.
            CV_ITER_FIXED_POINT - Fixed-Point iteration iteration.
                Advised to use together with argument cvode_linear_multistep_method=CV.ADAMS.

    cvodeLinearMultistepMethod : CV | None, optional
        Linear multistep method for CVODE solver (default CV.BDF). Valid values:
            CV.BDF - BDF linear multistep method for stiff problems.
                Use together with argument cvode_non_linear_solver_iter=CV_ITER.NEWTON or None.

            CV.ADAMS - Adams-Moulton linear multistep method for nonstiff problems.
                Use together with argument cvode_non_linear_solver_iter=CV_ITER.FIXED_POINT or None.

    cx : str | None, optional
        Specifies a csv-file with inputs as correlation coefficient matrix Cx for DataReconciliation

    daeMode : bool | None, optional
        Enables daeMode simulation if the model was compiled with the omc flag --daeMode and ida method is used.

    deltaXLinearize : float | None, optional
        Specifies the delta x value for numerical differentiation used by linearization.
        The default value is sqrt(DBL_EPSILON*2e1).

    deltaXSolver : float | None, optional
        Sspecifies the delta x value for numerical differentiation used by integration method.
        The default values is sqrt(DBL_EPSILON).

    embeddedServer : Literal["opc-da", "opc-ua"] | str | None, optional
        Enables an embedded server. Valid values:
            None - default, run without embedded server

            opc-da - Run with embedded OPC DA server (WIN32 only, uses proprietary OPC SC interface)

            opc-ua - Run with embedded OPC UA server (TCP port 4841 for now; will have its own configuration option later)

            str - Path to a shared object implementing the embedded server interface (requires access to internal OMC data-structures if you want to read or write data)

    embeddedServerPort : int | None, optional
        Sspecifies the port number used by the embedded server. The default value is 4841 if an embedded server is set.

    mat_sync : int | None, optional
        Syncs the mat file header after emitting every N time-points.

    emit_protected : bool | None, optional
        Emits protected variables to the result-file.

    eps : int | None, optional
        Specifies the number of convergence iteration to be performed for DataReconciliation.

    f : str | None, optional
        Specifies a new setup XML file to the generated simulation code.

    homAdaptBend : float | None, optional
        Maximum trajectory bending to accept the homotopy step.
        Default of 0.5 means the corrector vector has to be smaller than half of the predictor vector.

    homBacktraceStrategy : Literal["fix", "orthogonal"] | None, optional
        Specifies the backtrace strategy in the homotopy corrector step. Valid values:

            fix - default, go back to the path by fixing one coordinate

            orthogonal - go back to the path in an orthogonal direction to the tangent vector

    homHEps : float | None, optional
        Tolerance respecting residuals for the homotopy H-function (default: 1e-5).
        In the last step (lambda=1) newtonFTol is used as tolerance.

    homMaxLambdaSteps : int | None, optional
        Maximum lambda steps allowed to run the homotopy path (default: system size * 100).

    homMaxNewtonSteps : int | None, optional
        Maximum newton steps in the homotopy corrector step (default: 20).

    homMaxTries : int | None, optional
        Maximum number of tries for one homotopy lambda step (default: 10).

    homNegStartDir : bool, optional
        Start to run along the homotopy path in the negative direction.

        If one direction fails, the other direction is always used as fallback option.

    noHomotopyOnFirstTry : bool, optional
        If the model contains the homotopy operator, directly use the homotopy method
        to solve the initialization problem.

    homTauDecFac : float, optional
        Decrease homotopy step size tau by this factor if tau is
        too big in the homotopy corrector step (default: 10.0).

    homTauDecFacPredictor : float, optional
        Decrease homotopy step size tau by this factor if tau
        is too big in the homotopy predictor step (default: 2.0).

    homTauIncFac : float, optional
        Increase homotopy step size tau by this factor if tau
        can be increased after the homotopy corrector step (default: 2.0).

    homTauIncThreshold : float, optional
        Increase the homotopy step size tau if homAdaptBend/bend > homTauIncThreshold (default: 10).

    homTauMax : float, optional
        Maximum homotopy step size tau for the homotopy process (default: 10).

    homTauMin : float, optional
        Minimum homotopy step size tau for the homotopy process (default: 1e-4).

    homTauStart : float, optional
        Homotopy step size tau at the beginning of the homotopy process (default: 0.2).

    ils : int, optional
        Specifies the number of steps for homotopy method (required: initialisation_method='symbolic').
        The value is an Integer with default value 3.

    idaMaxErrorTestFails : int, optional
        Specifies the maximum number of error test failures in attempting one step.
        The default value is 7.

    idaMaxNonLinIters : int, optional
        Specifies the maximum number of nonlinear solver iterations at one step.
        The default value is 3.

    idaMaxConvFails : int, optional
        Specifies the maximum number of nonlinear solver convergence failures at one step.
        The default value is 10.

    idaNonLinConvCoef : float, optional
        Specifies the safety factor in the nonlinear convergence test. The default value is 0.33.

    idaLS : Literal["dense", "klu", "spgmr", "spbcg", "sptqmr"], optional
        Specifies the linear solver of the ida integration method. Valid values:

            dense (ida internal dense method.)

            klu (ida use sparse direct solver KLU. (default))

            spgmr (ida generalized minimal residual method. Iterative method)

            spbcg (ida Bi-CGStab. Iterative method)

            sptfqmr (ida TFQMR. Iterative method)

    idaScaling : bool, optional [-idaScaling]
        Enable scaling of the IDA solver.

    idaSensitivity : bool, optional
        Enables sensitivity analysis with respect to parameters if the
        model is compiled with omc flag --calculateSensitivities.

    ignoreHideResult : bool, optional [-ignoreHideResult]
        Emits also variables with HideResult=true annotation.

    iif : str, optional
        Specifies an external file for the initialization of the model.

    iim : Literal["none", "symbolic"], optional
        Specifies the initialization method. Following options are available: 'symbolic' (default) and 'none'.

            none (sets all variables to their start values and skips the initialization process)

            symbolic (solves the initialization problem symbolically - default)

    iit : float, optional
        Specifies a time for the initialization of the model.

    impRKOrder : int, optional
        Specifies the integration order of the implicit Runge-Kutta method.
        Valid values: 1 to 6. Default order is 5.

    impRKLS : Literal["iterativ", "dense"], optional
        Selects the linear solver of the integration methods impeuler, trapezoid and imprungekuta:

        iterativ - default, sparse iterativ linear solver with fallback case to dense solver

        dense - dense linear solver, SUNDIALS default method

    initialStepSize : float, optional
        Specifies an initial step size, used by the methods: dassl, ida, gbode

    csvInput : str, optional
        Specifies an csv-file with inputs for the simulation/optimization of the model

    stateFile : str, optional
        Specifies an file with states start values for the optimization of the model.

    ipopt_hesse : str, optional
        Specifies the hessematrix for Ipopt(OMC, BFGS, const).

    ipopt_init : str, optional [-ipopt_init=value]
        Specifies the initial guess for optimization (sim, const).

    ipopt_jac : str, optional [-ipopt_jac=value]
        Specifies the Jacobian for Ipopt(SYM, NUM, NUMDENSE).

    ipopt_max_iter : int, optional
        Specifies the max number of iteration for ipopt.

    ipopt_warm_start : int, optional
        Specifies lvl for a warm start in ipopt: 1,2,3,...

    jacobian : Literal["coloredNumerical", "internalNumerical", "coloredSymbolical", "numerical", "symbolical"], optional
        Select the calculation method for Jacobian used by the integration method:

        coloredNumerical (Colored numerical Jacobian, which is default for dassl and ida. With option -idaLS=klu a sparse matrix is used.)

        internalNumerical (Dense solver internal numerical Jacobian.)

        coloredSymbolical (Colored symbolical Jacobian. Needs omc compiler flag --generateSymbolicJacobian. With option -idaLS=klu a sparse matrix is used.)

        numerical (Dense numerical Jacobian.)

        symbolical (Dense symbolical Jacobian. Needs omc compiler flag --generateSymbolicJacobian.)

    jacobianThreads : int, optional
        Specifies the number of threads for jacobian evaluation in dassl or ida. The value is an Integer with default value 1.

    l : float, optional [-l=value]
        Specifies a time where the linearization of the model should be performed.

    l_datarec : bool, optional [-l_datarec]
        Emit data recovery matrices with model linearization.

    logFormat : Literal["text", "xml", "xmltcp"], optional
        Specifies the log format of the executable:

            text (default)

            xml

            xmltcp (required -port flag)

    ls : Literal["lapack", "lis", "klu", "umfpack", "totalpivot", "default"], optional [-ls=value]
        Specifies the linear solver method

            lapack (method using LAPACK LU factorization)

            lis (method using iterative solver Lis)

            klu (method using KLU sparse linear solver)

            umfpack (method using UMFPACK sparse linear solver)

            totalpivot (method using a total pivoting LU factorization for underdetermination systems)

            default (default method - LAPACK with total pivoting as fallback)

    ls_ipopt : str, optional
        Specifies the linear solver method for Ipopt, default mumps.
        Note: Use if you build ipopt with other linear solver like ma27

    lss : Literal["default", "lis", "klu", "umfpack"], optional [-lss=value]
        Specifies the linear sparse solver method

            default (the default sparse linear solver (or a dense solver if there is none available) )

            lis (method using iterative solver Lis)

            klu (method using klu sparse linear solver)

            umfpack (method using umfpack sparse linear solver)

    lssMaxDensity : float, optional
        Specifies the maximum density for using a linear sparse solver. The value is a Double with default value 0.2.

    lssMinSize : int, optional
        Specifies the minimum system size for using a linear sparse solver. The value is an Integer with default value 1000.

    lvMaxWarn : int, optional
        Maximum number of times some repeating warnings are displayed. Default value 3.

    lv_time : (float, float), optional
        Specifies in which time interval logging is active.
        Doesn't affect LOG_STDOUT, LOG_ASSERT, and LOG_SUCCESS, LOG_STATS, LOG_STATS_V.

    lv_system : (int, ...), optional
        List of equation indices (available in the transformational debugger)
        for which solver logs are shown (by default logs for all systems are shown)

    mbi : int, optional
        Specifies the maximum number of bisection iterations for state event detection
        or zero for default behavior

    mei : int, optional
        Specifies the maximum number of event iterations.
        The value is an Integer with default value 20.

    maxIntegrationOrder : int, optional
        Specifies maximum integration order, used by the methods: dassl, ida.

    maxStepSize : float, optional
        Specifies maximum absolute step size, used by the methods: dassl, ida, gbode.

    measureTimePlotFormat : Literal['svg', 'jpg', 'ps', 'gif'], optional
        Specifies the output format of the measure time functionality

    newtonDiagnostics : bool, optional
        Implementation of "On the choice of initial guesses for the Newton-Raphson algorithm."
        See: https://doi.org/10.1016/j.amc.2021.125991

    newtonFTol : float, optional
        Tolerance respecting residuals for updating solution vector in Newton solver.
        Solution is accepted if the (scaled) 2-norm of the residuals is smaller than
        the tolerance newtonFTol and the (scaled) newton correction (delta_x)
        is smaller than the tolerance newtonXTol. The value is a Double with default value 1e-12.

    newtonMaxStepFactor : float, optional
        Maximum newton step factor mxnewtstep = maxStepFactor * norm2(xScaling). Used currently only by KINSOL.

    newtonXTol : float, optional
        Tolerance respecting newton correction (delta_x) for updating solution vector in Newton solver.
        Solution is accepted if the (scaled) 2-norm of the residuals is smaller than
        the tolerance newtonFTol and the (scaled) newton correction (delta_x) is
        smaller than the tolerance newtonXTol. The value is a Double with default value 1e-12.

    newton : Literal['damped', 'damped2', 'damped_ls', 'damped_bt'], optional
        Specifies the damping strategy for the newton solver.

            damped (Newton with a damping strategy)

            damped2 (Newton with a damping strategy 2)

            damped_ls (Newton with a damping line search)

            damped_bt (Newton with a damping backtracking and a minimum search via golden ratio method)

            pure (Newton without damping strategy)

    nls : Literal['hybrid', 'kinsol', 'kinsol', 'newton', 'mixed', 'homotopy'], optional
        Specifies the nonlinear solver:

            hybrid (Modification of the Powell hybrid method from minpack - former default solver)

            kinsol (SUNDIALS/KINSOL includes an interface to the sparse direct solver, KLU. See simulation option -nlsLS for more information.)

            newton (Newton Raphson - prototype implementation)

            mixed (Mixed strategy. First the homotopy solver is tried and then as fallback the hybrid solver.)

            homotopy (Damped Newton solver if failing case fixed-point and Newton homotopies are tried.)


    nlsInfo : bool, optional
        Outputs detailed information about solving process of non-linear systems into csv files.

    nlsLS : Literal['default', 'totalpivot', 'lapack', 'klu'], optional
        Specifies the linear solver used by the non-linear solver:

            default (chooses the nls linear solver based on which nls is being used.)

            totalpivot (internal total pivot implementation. Solve in some case even under-determined systems.)

            lapack (use external LAPACK implementation.)

            klu (use KLU direct sparse solver. Only with KINSOL available.)

    nlssMaxDensity : float, optional
        specifies the maximum density for using a non-linear sparse solver.
        The default value is 0.1

    nlssMinSize : int, optional
        Value specifies the minimum system size for using a non-linear sparse solver.
        The value is an Integer with default value 1000.

    noemit : bool, optional
       Do not emit any results to the result file.

    noEquidistantTimeGrid : bool, optional
       Output the internal steps given by dassl/ida instead of interpolating results
       into an equidistant time grid as given by stepSize or numberOfIntervals.

    noEquidistantOutputFrequency : int, optional
        Value 'n' controls the output frequency in noEquidistantTimeGrid mode
        and outputs every n-th time step

    noEquidistantOutputTime : float, optional
        Value timeValue controls the output time point in noEquidistantOutputTime
        mode and outputs every time>=k*timeValue, where k is an integer

    noEventEmit : bool, optional
        Do not emit event points to the result file.

    noRestart : bool, optional
        Disables the restart of the integration method after an event
        is performed, used by the methods: dassl, ida

    noRootFinding : bool, optional
        Disables the internal root finding procedure of methods: dassl and ida.

    noScaling : bool, optional
        Disables scaling for the variables and the residuals in the algebraic nonlinear solver KINSOL.

    noSuppressAlg : bool, optional
        Flag to not suppress algebraic variables in the local error test of the ida solver in daeMode.
        In general, the use of this option is discouraged when solving DAE systems of index 1,
        whereas it is generally encouraged for systems of index 2 or more.

    optDebugJac : int, optional
        Value specifies the number of iterations from the dynamic optimization,
        which will be debugged, creating .csv and .py files.

    optimizerNP : Literal[1, 3], optional
        Value specifies the number of points in a subinterval. Currently supports numbers 1 and 3.

    optimizerTimeGrid : str, optional
        Specifies external file with time points.

    output : list[str], optional
        Output the variables a, b and c at the end of the simulation to the standard output:
        time = value, a = value, b = value, c = value

    outputPath : str, optional
        Specifies a path for writing the output files i.e., model_res.mat, model_prof.intdata, model_prof.realdata etc.

    override : list[str], optional
        Override the variables or the simulation settings in the XML setup file For example:
        var1=start1,var2=start2,par3=start3,startTime=val1,stopTime=val2

    overrideFile : str, optional
        Will override the variables or the simulation settings in the XML setup file with the values from the file.
        Note that: overrideFile CANNOT be used with override. Use when variables for -override are too many. overrideFileName contains lines of the form: var1=start1

    port : int, optional
        Specifies the port for simulation status (default disabled).

    r : str, optional
        Specifies the name of the output result file. The default file-name is based on the model name and output format. For example: Model_res.mat.

    reconcile : bool, optional
        Run the Data Reconciliation numerical computation algorithm for constrained equations

    reconcileBoundaryConditions : bool, optional
        Run the Data Reconciliation numerical computation algorithm for boundary condition equations

    reconcileState : bool, optional
        Run the State Estimation numerical computation algorithm for constrained equations

    gbm : Literal[
        "adams",
        "expl_euler",
        "impl_euler",
        "trapezoid",
        "sdirk2",
        "sdirk3",
        "esdirk2",
        "esdirk3",
        "esdirk4",
        "radauIA2",
        "radauIA3",
        "radauIA4",
        "radauIIA2",
        "radauIIA3",
        "radauIIA4",
        "lobattoIIIA3",
        "lobattoIIIA4",
        "lobattoIIIB3",
        "lobattoIIIB4",
        "lobattoIIIC3",
        "lobattoIIIC4",
        "gauss2",
        "gauss3",
        "gauss4",
        "gauss5",
        "gauss6",
        "merson",
        "mersonSsc1",
        "mersonSsc2",
        "heun",
        "fehlberg12",
        "fehlberg45",
        "fehlberg78",
        "fehlbergSsc1",
        "fehlbergSsc2",
        "rk810",
        "rk1012",
        "rk1214",
        "dopri45",
        "dopriSsc1",
        "dopriSsc2",
        "tsit5",
        "rungekutta",
        "rungekuttaSsc"
    ], optional
        Specifies the chosen solver of solver gbode (single-rate, slow states integrator).

            adams (Implicit multistep method of type Adams-Moulton (order 2))

            expl_euler (Explizit Runge-Kutta Euler method (order 1))

            impl_euler (Implizit Runge-Kutta Euler method (order 1))

            trapezoid (Implicit Runge-Kutta trapezoid method (order 2))

            sdirk2 (Singly-diagonal implicit Runge-Kutta (order 2))

            sdirk3 (Singly-diagonal implicit Runge-Kutta (order 3))

            esdirk2 (Explicit singly-diagonal implicit Runge-Kutta (order 2))

            esdirk3 (Explicit singly-diagonal implicit Runge-Kutta (order 3))

            esdirk4 (Explicit singly-diagonal implicit Runge-Kutta (order 4))

            radauIA2 (Implicit Runge-Kutta method of Radau family IA (order 3))

            radauIA3 (Implicit Runge-Kutta method of Radau family IA (order 5))

            radauIA4 (Implicit Runge-Kutta method of Radau family IA (order 7))

            radauIIA2 (Implicit Runge-Kutta method of Radau family IIA (order 3))

            radauIIA3 (Implicit Runge-Kutta method of Radau family IIA (order 5))

            radauIIA4 (Implicit Runge-Kutta method of Radau family IIA (order 7))

            lobattoIIIA3 (Implicit Runge-Kutta method of Lobatto family IIIA (order 4))

            lobattoIIIA4 (Implicit Runge-Kutta method of Lobatto family IIIA (order 6))

            lobattoIIIB3 (Implicit Runge-Kutta method of Lobatto family IIIB (order 4))

            lobattoIIIB4 (Implicit Runge-Kutta method of Lobatto family IIIB (order 6))

            lobattoIIIC3 (Implicit Runge-Kutta method of Lobatto family IIIC (order 4))

            lobattoIIIC4 (Implicit Runge-Kutta method of Lobatto family IIIC (order 6))

            gauss2 (Implicit Runge-Kutta method of Gauss (order 4))

            gauss3 (Implicit Runge-Kutta method of Gauss (order 6))

            gauss4 (Implicit Runge-Kutta method of Gauss (order 8))

            gauss5 (Implicit Runge-Kutta method of Gauss (order 10))

            gauss6 (Implicit Runge-Kutta method of Gauss (order 12))

            merson (Explicit Runge-Kutta Merson method (order 4))

            mersonSsc1 (Explicit Runge-Kutta Merson method with large stability region (order 1))

            mersonSsc2 (Explicit Runge-Kutta Merson method with large stability region (order 2))

            heun (Explicit Runge-Kutta Heun method (order 2))

            fehlberg12 (Explicit Runge-Kutta Fehlberg method (order 2))

            fehlberg45 (Explicit Runge-Kutta Fehlberg method (order 5))

            fehlberg78 (Explicit Runge-Kutta Fehlberg method (order 8))

            fehlbergSsc1 (Explicit Runge-Kutta Fehlberg method with large stability region (order 1))

            fehlbergSsc2 (Explicit Runge-Kutta Fehlberg method with large stability region (order 2))

            rk810 (Explicit 8-10 Runge-Kutta method (order 10))

            rk1012 (Explicit 10-12 Runge-Kutta method (order 12))

            rk1214 (Explicit 12-14 Runge-Kutta method (order 14))

            dopri45 (Explicit Runge-Kutta method Dormand-Prince (order 5))

            dopriSsc1 (Explicit Runge-Kutta method Dormand-Prince with large stability region (order 1))

            dopriSsc2 (Explicit Runge-Kutta method Dormand-Prince with large stability region (order 2))

            tsit5 (Explicit Runge-Kutta method from Tsitouras (order 5))

            rungekutta (Explicit classical Runge-Kutta method (order 4))

            rungekuttaSsc (Explicit Runge-Kutta method with large stabiliy region (order 1))

    gbctrl : Literal["i", "pi", "pid", "const"], optional
        Step size control of solver gbode (single-rate, slow states integrator).

            i (I controller for step size)

            pi (PI controller for step size)

            pid (PID controller for step size)

            const (Constant step size)

    gberr : Literal["default", "richardson", "embedded"], optional
        Error estimation method for solver gbode (single-rate, slow states integrator) Possible values:

            default - depending on the Runge-Kutta method

            richardson - Richardson extrapolation

            embedded - Embedded scheme

    gbint : Literal["linear", "hermite", "hermite_a", "hermite_b", "hermite_errctrl", "dense_output", "dense_output_errctrl"], optional
        Interpolation method of solver gbode (single-rate, slow states integrator).

            linear (Linear interpolation (1st order))

            hermite (Hermite interpolation (3rd order))

            hermite_a (Hermite interpolation (only for left hand side))

            hermite_b (Hermite interpolation (only for right hand side))

            hermite_errctrl (Hermite interpolation with error control)

            dense_output (use dense output formula for interpolation)

            dense_output_errctrl (use dense output fomular with error control)

    gbfm : Literal[
            "adams",
            "expl_euler",
            "impl_euler",
            "trapezoid",
            "sdirk2",
            "sdirk3",
            "esdirk2",
            "esdirk3",
            "esdirk4",
            "radauIA2",
            "radauIA3",
            "radauIA4",
            "radauIIA2",
            "radaulIIA3",
            "radaulIIA4",
            "lobattoIIIA3",
            "lobattoIIIA4",
            "lobattoIIIB3",
            "lobattoIIIB4",
            "lobattoIIIC3",
            "lobattoIIIC4",
            "gauss2",
            "gauss3",
            "gauss4",
            "gauss5",
            "gauss6",
            "merson",
            "mersonSsc1",
            "mersonSsc2",
            "heun",
            "fehlberg12",
            "fehlberg45",
            "fehlberg78",
            "fehlbergSsc1",
            "fehlbergSsc2",
            "rk810",
            "rk1012",
            "dopri45",
            "dopriSsc1",
            "dopriSsc2",
            "tsit5",
            "rungekutta",
            "rungekuttaSsc",
        ], optional
            Specifies the chosen solver of solver gbode (multi-rate, fast states integrator). Current Restriction: Fully implicit (Gauss, Radau, Lobatto) RK methods are not supported, yet.

                adams (Implicit multistep method of type Adams-Moulton (order 2))

                expl_euler (Explizit Runge-Kutta Euler method (order 1))

                impl_euler (Implizit Runge-Kutta Euler method (order 1))

                trapezoid (Implicit Runge-Kutta trapezoid method (order 2))

                sdirk2 (Singly-diagonal implicit Runge-Kutta (order 2))

                sdirk3 (Singly-diagonal implicit Runge-Kutta (order 3))

                esdirk2 (Explicit singly-diagonal implicit Runge-Kutta (order 2))

                esdirk3 (Explicit singly-diagonal implicit Runge-Kutta (order 3))

                esdirk4 (Explicit singly-diagonal implicit Runge-Kutta (order 4))

                radauIA2 (Implicit Runge-Kutta method of Radau family IA (order 3))

                radauIA3 (Implicit Runge-Kutta method of Radau family IA (order 5))

                radauIA4 (Implicit Runge-Kutta method of Radau family IA (order 7))

                radauIIA2 (Implicit Runge-Kutta method of Radau family IIA (order 3))

                radauIIA3 (Implicit Runge-Kutta method of Radau family IIA (order 5))

                radauIIA4 (Implicit Runge-Kutta method of Radau family IIA (order 7))

                lobattoIIIA3 (Implicit Runge-Kutta method of Lobatto family IIIA (order 4))

                lobattoIIIA4 (Implicit Runge-Kutta method of Lobatto family IIIA (order 6))

                lobattoIIIB3 (Implicit Runge-Kutta method of Lobatto family IIIB (order 4))

                lobattoIIIB4 (Implicit Runge-Kutta method of Lobatto family IIIB (order 6))

                lobattoIIIC3 (Implicit Runge-Kutta method of Lobatto family IIIC (order 4))

                lobattoIIIC4 (Implicit Runge-Kutta method of Lobatto family IIIC (order 6))

                gauss2 (Implicit Runge-Kutta method of Gauss (order 4))

                gauss3 (Implicit Runge-Kutta method of Gauss (order 6))

                gauss4 (Implicit Runge-Kutta method of Gauss (order 8))

                gauss5 (Implicit Runge-Kutta method of Gauss (order 10))

                gauss6 (Implicit Runge-Kutta method of Gauss (order 12))

                merson (Explicit Runge-Kutta Merson method (order 4))

                mersonSsc1 (Explicit Runge-Kutta Merson method with large stability region (order 1))

                mersonSsc2 (Explicit Runge-Kutta Merson method with large stability region (order 2))

                heun (Explicit Runge-Kutta Heun method (order 2))

                fehlberg12 (Explicit Runge-Kutta Fehlberg method (order 2))

                fehlberg45 (Explicit Runge-Kutta Fehlberg method (order 5))

                fehlberg78 (Explicit Runge-Kutta Fehlberg method (order 8))

                fehlbergSsc1 (Explicit Runge-Kutta Fehlberg method with large stability region (order 1))

                fehlbergSsc2 (Explicit Runge-Kutta Fehlberg method with large stability region (order 2))

                rk810 (Explicit 8-10 Runge-Kutta method (order 10))

                rk1012 (Explicit 10-12 Runge-Kutta method (order 12))

                rk1214 (Explicit 12-14 Runge-Kutta method (order 14))

                dopri45 (Explicit Runge-Kutta method Dormand-Prince (order 5))

                dopriSsc1 (Explicit Runge-Kutta method Dormand-Prince with large stability region (order 1))

                dopriSsc2 (Explicit Runge-Kutta method Dormand-Prince with large stability region (order 2))

                tsit5 (Explicit Runge-Kutta method from Tsitouras (order 5))

                rungekutta (Explicit classical Runge-Kutta method (order 4))

                rungekuttaSsc (Explicit Runge-Kutta method with large stabiliy region (order 1))

    gbfctrl : Literal["i", "pi", "pid", "const"], optional
        Step size control of solver gbode (multi-rate, fast states integrator).

            i (I controller for step size)

            pi (PI controller for step size)

            pid (PID controller for step size)

            const (Constant step size)

    gbferr : Literal["default", "richardson", "embedded"], optional
        Error estimation method for solver gbode (multi-rate, fast states integrator) Possible values:

            default - depending on the Runge-Kutta method

            richardson - Richardson extrapolation

            embedded - Embedded scheme

    gbfint : Literal["linear", "hermite", "hermite_a", "hermite_b", "hermite_errctrl", "dense_output", "dense_output_errctrl"], optional
        Interpolation method of solver gbode (multi-rate, fast states integrator).

            linear (Linear interpolation (1st order))

            hermite (Hermite interpolation (3rd order))

            hermite_a (Hermite interpolation (only for left hand side))

            hermite_b (Hermite interpolation (only for right hand side))

            hermite_errctrl (Hermite interpolation with error control)

            dense_output (use dense output formula for interpolation)

            dense_output_errctrl (use dense output fomular with error control)

    gbfnls : Literal["newton", "kinsol"], optional
        Non-linear solver method of solver gbode (multi-rate, fast states integrator).

            newton (Newton method, dense)

            kinsol (SUNDIALS KINSOL: Inexact Newton, sparse)

    gbratio : float, optional
        Define percentage of states for the fast states selection of solver gbode (values from 0 to 1).

    rt : float, optional
        Value specifies the scaling factor for real-time synchronization (0 disables).
        A value > 1 means the simulation takes a longer time to simulate.

    s : Literal[
        "euler",
        "heun",
        "rungekutta",
        "impeuler",
        "trapezoid",
        "imprungekutta",
        "gbode",
        "irksco",
        "dassl",
        "ida",
        "cvode",
        "rungekuttaSsc",
        "symSolver",
        "symSolverSsc",
        "qss",
        "optimization"
    ], optional
        Specifies the integration method. For additional information see the User's Guide

            euler - Euler - explicit, fixed step size, order 1

            heun - Heun's method - explicit, fixed step, order 2

            rungekutta - classical Runge-Kutta - explicit, fixed step, order 4

            impeuler - Euler - implicit, fixed step size, order 1

            trapezoid - trapezoidal rule - implicit, fixed step size, order 2

            imprungekutta - Runge-Kutta methods based on Radau and Lobatto IIA - implicit, fixed step size, order 1-6(selected manually by flag -impRKOrder)

            gbode - generic bi-rate ODE solver - implicit, explicit, step size control, arbitrary order

            irksco - own developed Runge-Kutta solver - implicit, step size control, order 1-2

            dassl - default solver - BDF method - implicit, step size control, order 1-5

            ida - SUNDIALS IDA solver - BDF method with sparse linear solver - implicit, step size control, order 1-5

            cvode - experimental implementation of SUNDIALS CVODE solver - BDF or Adams-Moulton method - step size control, order 1-12

            rungekuttaSsc - Runge-Kutta based on Novikov (2016) - explicit, step size control, order 4-5 [experimental]

            symSolver - symbolic inline Solver [compiler flag +symSolver needed] - fixed step size, order 1

            symSolverSsc - symbolic implicit Euler with step size control [compiler flag +symSolver needed] - step size control, order 1

            qss - A QSS solver [experimental]

            optimization - Special solver for dynamic optimization

    single : bool, optional
        Output results in single precision (mat-format only).

    steps : bool, optional
        Dumps the number of integration steps into the result file.

    steadyState : bool, optional
        Aborts the simulation if steady state is reached.

    steadyStateTol : float, optional
        This relative tolerance is used to detect steady state: max(|d(x_i)/dt|/nominal(x_i)) < steadyStateTol

    sx : str, optional
        Value specifies an csv-file with inputs as covariance matrix Sx for DataReconciliation

    keepHessian : bool, optional
        Value specifies the number of steps, which keep Hessian matrix constant.

    w : bool, optional
        Shows all warnings even if a related log-stream is inactive.

    parmodNumThreads : int, optional
        Value specifies the number of threads for simulation using parmodauto. If not specified (or is 0) it will use the systems max number of threads.
        Note that this option is ignored if the model is not compiled with --parmodauto

    Logging Setup
    -------------

    LOG_STDOUT: bool, optional
        this stream is active by default

    LOG_ASSERT: bool, optional
        this stream is active by default

    LOG_DASSL: bool, optional
        additional information about dassl solver

    LOG_DASSL_STATES: bool, optional
        outputs the states at every dassl call)

    LOG_DEBUG: bool, optional
        additional debug information

    LOG_DELAY: bool, optional
        debug information for delay operator

    LOG_DIVISION: bool, optional
        Log division by zero

    LOG_DSS: bool, optional
        outputs information about dynamic state selection

    LOG_DSS_JAC: bool, optional
        outputs jacobian of the dynamic state selection

    LOG_DT: bool, optional
        additional information about dynamic tearing

    LOG_DT_CONS: bool, optional
        additional information about dynamic tearing (local and global constraints)

    LOG_EVENTS: bool, optional
        additional information during event iteration

    LOG_EVENTS_V: bool, optional
        verbose logging of event system

    LOG_GBODE: bool, optional
        information about GBODE solver

    LOG_GBODE_V: bool, optional
        verbose information about GBODE solve

    LOG_GBODE_NLS: bool, optional
        log non-linear solver process of GBODE solver

    LOG_GBODE_NLS_V: bool, optional
        verbose log non-linear solver process of GBODE solver

    LOG_GBODE_STATES: bool, optional
        output states at every GBODE call

    LOG_INIT: bool, optional
        additional information during initialization

    LOG_INIT_HOMOTOPY: bool, optional
        log homotopy initialization

    LOG_INIT_V: bool, optional
        verbose information during initialization

    LOG_IPOPT: bool, optional
        information from Ipopt

    LOG_IPOPT_FULL: bool, optional
        more information from Ipopt

    LOG_IPOPT_JAC: bool, optional
        check jacobian matrix with Ipopt

    LOG_IPOPT_HESSE: bool, optional
        check hessian matrix with Ipopt

    LOG_IPOPT_ERROR: bool, optional
        print max error in the optimization

    LOG_JAC: bool, optional
        outputs the jacobian matrix used by ODE solvers

    LOG_LS: bool, optional
        logging for linear systems

    LOG_LS_V: bool, optional
        verbose logging of linear systems

    LOG_MIXED: bool, optional
        logging for mixed systems

    LOG_NLS: bool, optional
        logging for nonlinear systems

    LOG_NLS_V: bool, optional
        verbose logging of nonlinear systems

    LOG_NLS_HOMOTOPY: bool, optional
        logging of homotopy solver for nonlinear systems

    LOG_NLS_JAC: bool, optional
        outputs the jacobian of nonlinear systems

    LOG_NLS_JAC_TEST: bool, optional
        tests the analytical jacobian of nonlinear systems

    LOG_NLS_NEWTON_DIAG: bool, optional
        Log Newton diagnostic

    LOG_NLS_RES: bool, optional
        outputs every evaluation of the residual function

    LOG_NLS_EXTRAPOLATE: bool, optional
        outputs debug information about extrapolate process

    LOG_RES_INIT: bool, optional
        outputs residuals of the initialization

    LOG_RT: bool, optional
        additional information regarding real-time processes

    LOG_SIMULATION: bool, optional
        additional information about simulation process

    LOG_SOLVER: bool, optional
        additional information about solver process

    LOG_SOLVER_V: bool, optional
        verbose information about the integration process

    LOG_SOLVER_CONTEXT: bool, optional
        context information during the solver process

    LOG_SOTI: bool, optional
        final solution of the initialization

    LOG_SPATIALDISTR: bool, optional
        logging of internal operations for spatialDistribution

    LOG_STATS: bool, optional
        additional statistics about timer/events/solver

    LOG_STATS_V: bool, optional
        additional statistics for LOG_STATS

    LOG_SUCCESS: bool, optional
        this stream is active by default

    LOG_SYNCHRONOUS: bool, optional
        log clocks and sub-clocks for synchronous features

    LOG_ZEROCROSSINGS: bool, optional
        additional information about the zerocrossings
    """

    abortSlowSimulation: bool = False
    alarm: pydantic.NonNegativeInt = 0
    clock: typing.Literal["RT", "CYC", "CPU"] | None = None
    cpu: bool = False
    csvOstep: pydantic.FilePath | None = None
    cvodeNonlinearSolverIteration: (
        typing.Literal["CV_ITER_NEWTON", "CV_ITER_FIXED_POINT"] | None
    ) = None
    cvodeLinearMultistepMethod: typing.Literal["CV_BDF", "CV_ADAMS"] | None = None
    cx: pydantic.FilePath | None = None
    daeMode: bool | None = None
    deltaXLinearize: pydantic.NonNegativeFloat | None = None
    deltaXSolver: pydantic.NonNegativeFloat | None = None
    embeddedServer: typing.Literal["opc-da", "opc-ua"] | pydantic.FilePath | None = None
    embeddedServerPort: int | None = None
    mat_sync: pydantic.PositiveInt | None = None
    emit_protected: bool | None = None
    eps: pydantic.PositiveInt | None = None
    f: pydantic.FilePath | None = None
    homAdaptBend: pydantic.PositiveFloat | None = None
    homBacktraceStrategy: typing.Literal["fix", "orthogonal"] | None = None
    homHEps: pydantic.PositiveFloat | None = None
    homMaxLambdaSteps: pydantic.PositiveInt | None = None
    homMaxNewtonSteps: pydantic.PositiveInt | None = None
    homMaxTries: pydantic.PositiveInt | None = None
    homNegStartDir: bool | None = None
    noHomotopyOnFirstTry: bool | None = None
    homTauDecFac: pydantic.PositiveFloat | None = None
    homTauDecFacPredictor: pydantic.PositiveFloat | None = None
    homTauIncFac: pydantic.PositiveFloat | None = None
    homTauIncThreshold: pydantic.PositiveFloat | None = None
    homTauMax: pydantic.PositiveFloat | None = None
    homTauMin: pydantic.PositiveFloat | None = None
    homTauStart: pydantic.PositiveFloat | None = None
    ils: pydantic.PositiveInt | None = None
    idaMaxErrorTestFails: pydantic.PositiveInt | None = None
    idaMaxNonLinIters: pydantic.PositiveInt | None = None
    idaMaxConvFails: pydantic.PositiveInt | None = None
    idaNonLinConvCoef: pydantic.PositiveFloat | None = None
    idaLS: typing.Literal["dense", "klu", "spgmr", "spbcg", "sptqmr"] | None = None
    idaScaling: bool | None = None
    idaSensitivity: bool | None = None
    ignoreHideResult: bool | None = None
    iif: pydantic.FilePath | None = None
    iim: typing.Literal["none", "symbolic"] | None = None
    iit: pydantic.NonNegativeFloat | None = None
    impRKOrder: pydantic.confloat(ge=1, le=6) | None = None
    impRKLS: typing.Literal["iterativ", "dense"] | None = None
    initialStepSize: pydantic.PositiveFloat | None = None
    csvInput: pydantic.FilePath | None = None
    stateFile: pydantic.FilePath | None = None
    ipopt_hesse: str | None = None  # TODO: Unknown type
    ipopt_init: str | None = None  # TODO: Unknown type
    ipopt_jac: str | None = None  # TODO: Unknown type
    ipopt_max_iter: pydantic.PositiveInt | None = None
    ipopt_warm_start: pydantic.PositiveInt | None = None
    jacobian: (
        typing.Literal[
            "coloredNumerical",
            "internalNumerical",
            "coloredSymbolical",
            "numerical",
            "symbolical",
        ]
        | None
    ) = None
    jacobianThreads: pydantic.PositiveInt | None = None
    l: pydantic.NonNegativeFloat | None = None
    l_data_rec: bool | None = None
    logFormat: typing.Literal["text", "xml", "xmltcp"] | None = None
    ls: (
        typing.Literal["lapack", "lis", "klu", "umfpack", "totalpivot", "default"]
        | None
    ) = None
    ls_ipopt: str | None = None
    lss: typing.Literal["default", "lis", "klu", "umfpack"] | None = None
    lssMaxDensity: pydantic.PositiveFloat | None = None
    lssMinSize: pydantic.PositiveInt | None = None
    lvMaxWarn: pydantic.PositiveInt | None = None
    lv_time: (
        pydantic.conlist(max_length=2, min_length=2, item_type=pydantic.PositiveFloat)
        | None
    ) = None
    lv_system: tuple[pydantic.NonNegativeInt] | None = None
    mbi: pydantic.PositiveInt | None = None
    mei: pydantic.PositiveInt | None = None
    maxIntegrationOrder: pydantic.PositiveInt | None = None
    maxStepSize: pydantic.PositiveFloat | None = None
    measureTimePlotFormat: typing.Literal["svg", "jpg", "ps", "gif"] | None = None
    newtonDiagnostics: bool | None = None
    newtonFTol: pydantic.PositiveFloat | None = None
    newtonMaxStepFactor: float | None = None
    newtonXTol: pydantic.PositiveFloat | None = None
    newton: typing.Literal["damped", "damped2", "damped_ls", "damped_bt"] | None = None
    nls: (
        typing.Literal["hybrid", "kinsol", "kinsol", "newton", "mixed", "homotopy"]
        | None
    ) = None
    nlsInfo: bool | None = None
    nlsLS: typing.Literal["default", "totalpivot", "lapack", "klu"] | None = None
    nlssMaxDensity: pydantic.PositiveFloat | None = None
    nlssMinSize: pydantic.PositiveInt | None = None
    noemit: bool | None = None
    noEquidistantTimeGrid: bool | None = None
    noEquidistantOutputFrequency: pydantic.PositiveInt | None = None
    noEquidistantOutputTime: pydantic.PositiveFloat | None = None
    noEventEmit: bool | None = None
    noRestart: bool | None = None
    noRootFinding: bool | None = None
    noScaling: bool | None = None
    noSuppressAlg: bool | None = None
    optDebugJac: pydantic.PositiveInt | None = None
    optimizerNP: typing.Literal[1, 3] | None = None
    optimizerTimeGrid: pydantic.FilePath | None = None
    output: list[str] | None = None
    outputPath: pydantic.DirectoryPath | None = None
    override: list[str] | None = None
    overrideFile: pydantic.FilePath | None = None
    port: pydantic.PositiveInt | None = None
    r: str | None = None
    reconcile: bool | None = None
    reconcileBoundaryConditions: bool | None = None
    reconcileState: bool | None = None
    gbm: (
        typing.Literal[
            "adams",
            "expl_euler",
            "impl_euler",
            "trapezoid",
            "sdirk2",
            "sdirk3",
            "esdirk2",
            "esdirk3",
            "esdirk4",
            "radauIA2",
            "radauIA3",
            "radauIA4",
            "radauIIA2",
            "radauIIA3",
            "radauIIA4",
            "lobattoIIIA3",
            "lobattoIIIA4",
            "lobattoIIIB3",
            "lobattoIIIB4",
            "lobattoIIIC3",
            "lobattoIIIC4",
            "gauss2",
            "gauss3",
            "gauss4",
            "gauss5",
            "gauss6",
            "merson",
            "mersonSsc1",
            "mersonSsc2",
            "heun",
            "fehlberg12",
            "fehlberg45",
            "fehlberg78",
            "fehlbergSsc1",
            "fehlbergSsc2",
            "rk810",
            "rk1012",
            "rk1214",
            "dopri45",
            "dopriSsc1",
            "dopriSsc2",
            "tsit5",
            "rungekutta",
            "rungekuttaSsc",
        ]
        | None
    ) = None
    gbctrl: typing.Literal["i", "pi", "pid", "const"] | None = None
    gberr: typing.Literal["default", "richardson", "embedded"] | None = None
    gbint: (
        typing.Literal[
            "linear",
            "hermite",
            "hermite_a",
            "hermite_b",
            "hermite_errctrl",
            "dense_output",
            "dense_output_errctrl",
        ]
        | None
    ) = None
    gbnls: typing.Literal["newton", "kinsol"] | None = None
    gbfm: (
        typing.Literal[
            "adams",
            "expl_euler",
            "impl_euler",
            "trapezoid",
            "sdirk2",
            "sdirk3",
            "esdirk2",
            "esdirk3",
            "esdirk4",
            "radauIA2",
            "radauIA3",
            "radauIA4",
            "radauIIA2",
            "radaulIIA3",
            "radaulIIA4",
            "lobattoIIIA3",
            "lobattoIIIA4",
            "lobattoIIIB3",
            "lobattoIIIB4",
            "lobattoIIIC3",
            "lobattoIIIC4",
            "gauss2",
            "gauss3",
            "gauss4",
            "gauss5",
            "gauss6",
            "merson",
            "mersonSsc1",
            "mersonSsc2",
            "heun",
            "fehlberg12",
            "fehlberg45",
            "fehlberg78",
            "fehlbergSsc1",
            "fehlbergSsc2",
            "rk810",
            "rk1012",
            "dopri45",
            "dopriSsc1",
            "dopriSsc2",
            "tsit5",
            "rungekutta",
            "rungekuttaSsc",
        ]
        | None
    ) = None
    gbfctrl: typing.Literal["i", "pi", "pid", "const"] | None = None
    gbferr: typing.Literal["default", "richardson", "embedded"] | None = None
    gbfint: (
        typing.Literal[
            "linear",
            "hermite",
            "hermite_a",
            "hermite_b",
            "hermite_errctrl",
            "dense_output",
            "dense_output_errctrl",
        ]
        | None
    ) = None
    gbfnls: typing.Literal["newton", "kinsol"] | None = None
    s: (
        typing.Literal[
            "euler",
            "heun",
            "rungekutta",
            "impeuler",
            "trapezoid",
            "imprungekutta",
            "gbode",
            "irksco",
            "dassl",
            "ida",
            "cvode",
            "rungekuttaSsc",
            "symSolver",
            "symSolverSsc",
            "qss",
            "optimization",
        ]
        | None
    ) = None
    single: bool | None = None
    steps: bool | None = None
    steadyState: bool | None = None
    steadyStateTol: pydantic.PositiveFloat | None = None
    sx: pydantic.FilePath | None = None
    keepHessian: pydantic.PositiveInt | None = None
    w: bool | None = None
    parmodNumThreads: pydantic.PositiveInt | None = None
    LOG_STDOUT: bool | None = None
    LOG_ASSERT: bool | None = None
    LOG_DASSL: bool | None = None
    LOG_DASSL_STATES: bool | None = None
    LOG_DEBUG: bool | None = None
    LOG_DELAY: bool | None = None
    LOG_DIVISION: bool | None = None
    LOG_DSS: bool | None = None
    LOG_DSS_JAC: bool | None = None
    LOG_DT: bool | None = None
    LOG_DT_CONS: bool | None = None
    LOG_EVENTS: bool | None = None
    LOG_EVENTS_V: bool | None = None
    LOG_GBODE: bool | None = None
    LOG_GBODE_V: bool | None = None
    LOG_GBODE_NLS: bool | None = None
    LOG_GBODE_NLS_V: bool | None = None
    LOG_GBODE_STATES: bool | None = None
    LOG_INIT: bool | None = None
    LOG_INIT_HOMOTOPY: bool | None = None
    LOG_INIT_V: bool | None = None
    LOG_IPOPT: bool | None = None
    LOG_IPOPT_FULL: bool | None = None
    LOG_IPOPT_JAC: bool | None = None
    LOG_IPOPT_HESSE: bool | None = None
    LOG_IPOPT_ERROR: bool | None = None
    LOG_JAC: bool | None = None
    LOG_LS: bool | None = None
    LOG_LS_V: bool | None = None
    LOG_MIXED: bool | None = None
    LOG_NLS: bool | None = None
    LOG_NLS_V: bool | None = None
    LOG_NLS_HOMOTOPY: bool | None = None
    LOG_NLS_JAC: bool | None = None
    LOG_NLS_JAC_TEST: bool | None = None
    LOG_NLS_NEWTON_DIAG: bool | None = None
    LOG_NLS_RES: bool | None = None
    LOG_NLS_EXTRAPOLATE: bool | None = None
    LOG_RES_INIT: bool | None = None
    LOG_RT: bool | None = None
    LOG_SIMULATION: bool | None = None
    LOG_SOLVER: bool | None = None
    LOG_SOLVER_V: bool | None = None
    LOG_SOLVER_CONTEXT: bool | None = None
    LOG_SOTI: bool | None = None
    LOG_SPATIALDISTR: bool | None = None
    LOG_STATS: bool | None = None
    LOG_STATS_V: bool | None = None
    LOG_SUCCESS: bool | None = None
    LOG_SYNCHRONOUS: bool | None = None
    LOG_ZEROCROSSINGS: bool | None = None
    max_warn: int | None = None

    @pydantic.model_validator(mode="before")
    @classmethod
    def check_embedded_server_port(
        cls, values: dict[str, typing.Any] | None
    ) -> dict[str, typing.Any] | None:
        if (
            isinstance(values, dict)
            and values.get("embedded_server_port")
            and not values.get("embedded_server")
        ):
            raise AssertionError(
                "Cannot specify embedded server port without specifying value for 'embedded_server'"
            )
        return values

    @pydantic.model_validator(mode="before")
    @classmethod
    def check_homotopy_steps_and_symbolic(
        cls, values: dict[str, typing.Any] | None
    ) -> dict[str, typing.Any] | None:
        if (
            values
            and values.get("homotopy_n_steps") is not None
            and (_init_method := values.get("initialisation_method")) is not None
            and _init_method != "symbolic"
        ):
            raise AssertionError(
                f"Cannot specify 'homotopy_n_steps' with initialisation_method={_init_method}"
            )
        return values

    @pydantic.model_validator(mode="before")
    @classmethod
    def check_override_override_file(
        cls, values: dict[str, typing.Any] | None
    ) -> dict[str, typing.Any] | None:
        if values and values.get("override") is not None and values.get("overrideFile"):
            raise AssertionError("Cannot specify both 'override' and 'overrideFile'")
        return values

    def assemble_args(self) -> list[str]:
        _args_list: list[str] = []
        _log_levels_list: list[str] = []
        for arg_name, arg in self.model_dump().items():
            if not arg:
                continue
            if arg_name.startswith("LOG_"):
                _log_levels_list.append(f"{'-' if not arg else ''}{arg_name}")
            elif isinstance(arg, bool):
                _args_list.append(f"-{arg_name}")
            elif isinstance(arg, (list, tuple)):
                _args_list.append(f"-{arg_name}=" + ",".join(*arg))
            else:
                _args_list.append(f"-{arg_name}={arg}")

        if _log_levels_list:
            _args_list.append(f"-lv={','.join(_log_levels_list)}")

        return _args_list

    @property
    def inputPath(self) -> None:
        raise AssertionError(
            "Cannot access argument 'inputPath', this is used internally by Pydelica "
            "to setup simulations"
        )

    @inputPath.setter
    def inputPath(self, _) -> None:
        raise AssertionError(
            "Cannot set argument 'inputPath', this is used internally by Pydelica "
            "to setup simulations"
        )
