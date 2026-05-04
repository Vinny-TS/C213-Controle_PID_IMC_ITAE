import control as ctrl
import numpy as np

class logicaPID():
    # Método de Identificação de Smith
    @staticmethod
    def smith(tempo, degrau, temperatura):
        # Calcular ganho estático
        amplitudeInicial = temperatura[0]
        temperatura = temperatura - amplitudeInicial
        valorFinal = temperatura[-1]
        amplitudeDegrau = np.mean(degrau)
        k = valorFinal/amplitudeDegrau # k - ganho estático

        # Cálculo de t1 e t2
        t1 = tempo[np.where(temperatura >= 0.283 * valorFinal)[0][0]]
        t2 = tempo[np.where(temperatura >= 0.632 * valorFinal)[0][0]]

        # Calcular constante de tempo e atraso de transporte
        tau = 1.5*(t2-t1)
        theta = t2-tau

        return k, tau, theta, amplitudeInicial, amplitudeDegrau
    
    # Método de Identificação se Sundaresan
    @staticmethod
    def sundaresan(tempo, degrau, temperatura):
        # Calcular ganho estático
        amplitudeInicial = temperatura[0]
        temperatura = temperatura - amplitudeInicial
        valorFinal = temperatura[-1]
        amplitudeDegrau = np.mean(degrau)
        k = valorFinal/amplitudeDegrau # k - ganho estático

        # Cálculo de t1 e t2
        t1 = tempo[np.where(temperatura >= 0.353 * valorFinal)[0][0]]
        t2 = tempo[np.where(temperatura >= 0.853 * valorFinal)[0][0]]

        # Calcular constante de tempo e atraso de transporte
        tau = (2/3)*(t2-t1)
        theta = 1.3*t1 - 0.29*t2

        return k, tau, theta, amplitudeInicial, amplitudeDegrau
    
    # Erro Quadrático Médio
    @staticmethod
    def eqm(y_modelo, y_experimental):
        eqm = np.sqrt(np.sum((y_modelo - y_experimental) ** 2) / len(y_modelo))
        return eqm
    
    # Método IMC (Internal Model Control)
    @staticmethod
    def metodo_imc(k, tau, theta, lambda_c=None):
        # lambda_c é o parâmetro de sintonia (constante de tempo de malha fechada desejada)
        # Um bom valor padrão para robustez e velocidade para FOPDT é igual ao tempo morto (theta)
        if lambda_c is None:
            lambda_c = theta

        # Utilizando a aproximação de Padé de 1ª ordem para o tempo morto:
        Kp = (tau + 0.5 * theta) / (k * (lambda_c + 0.5 * theta))
        Ti = tau + 0.5 * theta
        Td = (tau * theta) / (2 * tau + theta)

        return Kp, Ti, Td
    
    # Método ITAE
    @staticmethod
    def metodo_itae(k, tau, theta):
        # Constantes
        A = 0.965
        B = -0.85
        C = 0.796
        D = -0.147
        E = 0.308
        F = 0.929

        # Calcular parâmetros
        Kp = (A/k)*((theta/tau)**B)
        Ti = tau/(C+D*(theta/tau))
        Td = tau*E*((theta/tau)**F)

        return Kp, Ti, Td
    
    # Métricas do Sistema
    @staticmethod
    def calcular_metricas(Kp, Ti, Td, sp, sistemaControle):
        PID = ctrl.tf([Kp*Td, Kp, Kp/Ti], [1, 0])
        Cs = ctrl.series(PID, sistemaControle)
        amplitudeDegrau = sp

        # Simulação do degrau e correção da Amplitude pelo SetPoint
        [Tempo, Amplitude] = ctrl.step_response(ctrl.feedback(Cs))
        Amplitude = Amplitude * sp

        infos_PID = ctrl.step_info(ctrl.feedback(Cs))
        regimePermanente = Amplitude[-1]

        # Pegar informações da métrica
        tr = infos_PID.get("RiseTime")
        ts = infos_PID.get("SettlingTime")
        mp = infos_PID.get("Overshoot")
        erro = amplitudeDegrau - regimePermanente

        return ts, tr, mp, erro
    
    # Sistema de Controle em Malha Aberta e Fechada
    @staticmethod
    def criar_modelo_sistema_controle(tempo, degrau, temperatura, metodo):
        if(metodo == "Smith"):
            k, tau, theta, amplitudeInicial, amplitudeDegrau = logicaPID.smith(tempo, degrau, temperatura)
        else:
            k, tau, theta, amplitudeInicial, amplitudeDegrau = logicaPID.sundaresan(tempo, degrau, temperatura)

        # Criar modelo do Sistema de Controle com os parâmetros identificados
        sistemaControle = ctrl.tf(k, [tau, 1])

        # Aproximação de Padé para atraso
        [num, den] = ctrl.pade(theta, 20)
        sys_pade = ctrl.tf(num, den)

        sistemaControle = ctrl.series(sistemaControle, sys_pade)

        # Resposta em malha aberta
        tempoAberta, temperaturaAberta = ctrl.step_response(sistemaControle, tempo)
        temperaturaAberta *= amplitudeDegrau

        # Resposta em malha fechada
        sistemaFechado = ctrl.feedback(sistemaControle, 1)
        tempoFechada, temperaturaFechada = ctrl.step_response(sistemaFechado, tempo)
        temperaturaFechada *= amplitudeDegrau

        return k, tau, theta, sistemaControle, tempoAberta, temperaturaAberta, tempoFechada, temperaturaFechada
    
    # Sistema com Controle PID
    @staticmethod
    def criar_sistema_controle_pid(Kp, Ti, Td, sys_atraso, sp):
        # Criar sistema com controle PID
        PID = ctrl.tf([Kp*Td, Kp, Kp/Ti], [1,0])
        t, y = ctrl.step_response(ctrl.feedback(ctrl.series(PID, sys_atraso), 1)*sp)

        return t, y
    
    # Verificação de Estabilidade em Malha Fechada
    @staticmethod
    def verificar_estabilidade(Kp, Ti, Td, sys_atraso):
        try:
            if Ti <= 0:
                return False
                
            PID = ctrl.tf([Kp*Td, Kp, Kp/Ti], [1, 0])
            
            sys_fechado = ctrl.feedback(ctrl.series(PID, sys_atraso), 1)
            
            polos = sys_fechado.poles()
            
            return all(np.real(p) < 0 for p in polos)
        except Exception:
            return False
