workspace "Sistema Bancario - Casos de Uso" "Diagrama de casos de uso del sistema bancario fintech" {

    model {
        # Actores
        cliente = person "Cliente" "Usuario del sistema bancario que realiza operaciones financieras"
        sistema = softwareSystem "Sistema Bancario" "Sistema fintech que gestiona cuentas, transacciones y reglas de negocio" {
            
            # Casos de uso principales
            crearCliente = container "Crear Cliente" "Registra un nuevo cliente en el sistema con nombre y email único" {
                tags "UseCase"
            }
            
            crearCuenta = container "Crear Cuenta" "Crea una nueva cuenta/wallet para un cliente existente" {
                tags "UseCase"
            }
            
            depositar = container "Depositar" "Deposita dinero en una cuenta, aplicando comisiones y validaciones" {
                tags "UseCase"
            }
            
            retirar = container "Retirar" "Retira dinero de una cuenta, validando fondos suficientes y aplicando comisiones" {
                tags "UseCase"
            }
            
            transferir = container "Transferir" "Transfiere dinero entre dos cuentas de forma atómica" {
                tags "UseCase"
            }
            
            consultarSaldo = container "Consultar Saldo" "Consulta el saldo y detalles de una cuenta" {
                tags "UseCase"
            }
            
            listarTransacciones = container "Listar Transacciones" "Lista el historial de transacciones de una cuenta" {
                tags "UseCase"
            }
            
            # Casos de uso de validación (includes)
            calcularComision = container "Calcular Comisión" "Calcula la comisión según la estrategia configurada (plana, porcentual, escalonada)" {
                tags "ValidationUseCase"
            }
            
            validarRiesgo = container "Validar Reglas de Riesgo" "Valida reglas de fraude: monto máximo, velocidad, límite diario" {
                tags "ValidationUseCase"
            }
            
            validarFondos = container "Validar Fondos Suficientes" "Verifica que la cuenta tenga saldo suficiente para la operación" {
                tags "ValidationUseCase"
            }
            
            registrarLedger = container "Registrar en Ledger" "Crea asientos contables de doble entrada en el ledger" {
                tags "ValidationUseCase"
            }
        }
        
        # Relaciones Cliente -> Casos de Uso
        cliente -> crearCliente "Registra sus datos personales"
        cliente -> crearCuenta "Solicita apertura de cuenta"
        cliente -> depositar "Deposita fondos"
        cliente -> retirar "Retira efectivo"
        cliente -> transferir "Transfiere a otra cuenta"
        cliente -> consultarSaldo "Consulta balance actual"
        cliente -> listarTransacciones "Revisa historial"
        
        # Relaciones Include (casos de uso que incluyen validaciones)
        depositar -> calcularComision "<<include>>"
        depositar -> validarRiesgo "<<include>>"
        depositar -> registrarLedger "<<include>>"
        
        retirar -> calcularComision "<<include>>"
        retirar -> validarRiesgo "<<include>>"
        retirar -> validarFondos "<<include>>"
        retirar -> registrarLedger "<<include>>"
        
        transferir -> calcularComision "<<include>>"
        transferir -> validarRiesgo "<<include>>"
        transferir -> validarFondos "<<include>>"
        transferir -> registrarLedger "<<include>>"
        
        # Relaciones Extend (casos de uso extendidos)
        crearCuenta -> crearCliente "<<extend>> Si el cliente no existe"
    }

    views {
        systemContext sistema "UseCaseDiagram" {
            include *
            autoLayout
            description "Diagrama de casos de uso del sistema bancario MVP mostrando todas las operaciones disponibles para el cliente"
        }

        styles {
            element "Person" {
                shape Person
                background #08427b
                color #ffffff
            }
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "UseCase" {
                shape Ellipse
                background #85bbf0
                color #000000
            }
            element "ValidationUseCase" {
                shape Ellipse
                background #cfe2f3
                color #000000
            }
        }

        theme default
    }
}
