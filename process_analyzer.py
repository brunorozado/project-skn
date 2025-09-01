import pandas as pd
from pm4py.convert import convert_to_event_log
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments_factory
from pm4py.algo.analysis.bottleneck import algorithm as bottleneck_analysis
from bpmn_python.bpmn_diagram_layouter import BPMNVisualLayouter
from bpmn_python.bpmn_diagram_metrics import BPMNMetrics
from bpmn_python.bpmn_diagram_properties import BPMNProperties
from bpmn_python.bpmn_diagram_rep import BPMNDiagram

class ProcessAnalyzer:
    def __init__(self, log_path):
        self.log_path = log_path
        self.event_log = None

    def load_and_convert_log(self):
        """Carrega o log de eventos de um CSV e o converte para o formato PM4Py."""
        print(f"Carregando log de eventos de {self.log_path}...")
        dataframe = pd.read_csv(self.log_path, parse_dates=["timestamp"], dtype={
            'case_id': str,
            'activity': str
        })
        # Renomear colunas para o padrão PM4Py
        dataframe.rename(columns={
            'case_id': 'case:concept:name',
            'activity': 'concept:name',
            'timestamp': 'time:timestamp'
        }, inplace=True)
        self.event_log = convert_to_event_log(dataframe)
        print("Log de eventos carregado e convertido.")
        return self.event_log

    def discover_process_model(self):
        """Descobre o modelo de processo usando o Alpha Miner."""
        if self.event_log is None:
            self.load_and_convert_log()

        print("Descobrindo modelo de processo com Alpha Miner...")
        net, initial_marking, final_marking = alpha_miner.apply(self.event_log)
        print("Modelo de processo descoberto.")
        return net, initial_marking, final_marking

    def visualize_process_model(self, net, initial_marking, final_marking, output_path="process_model.png"):
        """Visualiza o modelo de processo e salva como imagem."""
        print(f"Visualizando modelo de processo e salvando em {output_path}...")
        gviz = pn_visualizer.apply(net, initial_marking, final_marking)
        pn_visualizer.save(gviz, output_path)
        print("Modelo de processo visualizado e salvo.")

    def analyze_conformance(self, net, initial_marking, final_marking):
        """Analisa a conformidade do log de eventos com o modelo de processo."""
        if self.event_log is None:
            self.load_and_convert_log()

        print("Analisando conformidade...")
        aligned_traces = alignments_factory.apply(self.event_log, net, initial_marking, final_marking)
        print(f"Número de traces alinhados: {len(aligned_traces)}")
        num_aligned = sum(1 for trace in aligned_traces if trace["fitness"] == 1.0)
        print(f"Traces com fitness perfeito: {num_aligned}/{len(aligned_traces)}")
        return aligned_traces

    def identify_bottlenecks(self):
        """Identifica gargalos no processo usando o PM4Py."""
        if self.event_log is None:
            self.load_and_convert_log()

        print("Identificando gargalos...")
        # A função bottleneck_analysis.apply espera um event log
        bottlenecks = bottleneck_analysis.apply(self.event_log)

        bottleneck_info = []
        if bottlenecks:
            for activity, metrics in bottlenecks.items():
                bottleneck_info.append(f"Atividade: {activity}, Tempo Médio de Espera: {metrics.get('avg_waiting_time', 'N/A')}, Tempo Médio de Serviço: {metrics.get('avg_service_time', 'N/A')}")
        else:
            bottleneck_info.append("Nenhum gargalo significativo identificado.")
        return bottleneck_info

    def generate_bpmn_xml_content(self, net, initial_marking, final_marking):
        """Gera o conteúdo de um arquivo BPMN 2.0 XML a partir do modelo de processo."""
        print("Gerando conteúdo BPMN 2.0 XML...")
        
        bpmn_diagram = BPMNDiagram()
        process_id = "Process_1"
        process_name = "Processo Descoberto"
        bpmn_diagram.add_process_to_diagram(process_id, process_name)

        activities = self.event_log["concept:name"].unique()
        for activity in activities:
            bpmn_diagram.add_task_to_process(process_id, activity, activity)

        start_event_id = "StartEvent_1"
        start_event_name = "Início"
        bpmn_diagram.add_start_event_to_process(process_id, start_event_id, start_event_name)

        end_event_id = "EndEvent_1"
        end_event_name = "Fim"
        bpmn_diagram.add_end_event_to_process(process_id, end_event_id, end_event_name)

        if len(activities) > 0:
            bpmn_diagram.add_sequence_flow_to_process(process_id, start_event_id, activities[0])
            for i in range(len(activities) - 1):
                bpmn_diagram.add_sequence_flow_to_process(process_id, activities[i], activities[i+1])
            bpmn_diagram.add_sequence_flow_to_process(process_id, activities[-1], end_event_id)

        # Retorna o conteúdo XML como string
        return bpmn_diagram.get_xml_as_string()

    def generate_sankhya_flow_script(self, bottlenecks):
        script_content = "// Script de Automação Sankhya Flow gerado por IA\n\n"
        script_content += "// Este script pode ser usado para automatizar otimizações de processos identificadas.\n\n"

        if bottlenecks:
            script_content += "// Gargalos identificados e sugestões de otimização:\n"
            for bottleneck in bottlenecks:
                script_content += f"// {bottleneck}\n"
                if "Atividade: " in bottleneck:
                    activity_name = bottleneck.split("Atividade: ")[1].split(",")[0].strip()
                    script_content += f"// Exemplo de automação para a atividade \'{activity_name}\':\n"
                    script_content += f"// var query = getQuery();\n"
                    script_content += f"// query.nativeSelect(\"SELECT * FROM TGFTAB WHERE DESCRICAO = \\'{activity_name}\\'\");\n"
                    script_content += f"// if (query.next()) {{ \n"
                    script_content += f"//     mensagem = \'Atividade {activity_name} encontrada. Iniciando otimização...\';\n"
                    script_content += f"//     // Adicione aqui a lógica de automação específica para a otimização desta atividade\n"
                    script_content += f"// }} else {{ \n"
                    script_content += f"//     mostraErro(\'Atividade {activity_name} não encontrada para otimização.\');\n"
                    script_content += f"// }}\n\n"
        else:
            script_content += "// Nenhum gargalo significativo identificado para gerar automações.\n"

        script_content += "// Para mais informações sobre as APIs JavaScript do Sankhya, consulte a documentação oficial.\n"
        return script_content

if __name__ == '__main__':
    analyzer = ProcessAnalyzer(log_path="sankhya_processed_data.csv")
    event_log = analyzer.load_and_convert_log()
    net, initial_marking, final_marking = analyzer.discover_process_model()
    # analyzer.visualize_process_model(net, initial_marking, final_marking)
    # analyzer.generate_bpmn_xml(net, initial_marking, final_marking)
    # aligned_traces = analyzer.analyze_conformance(net, initial_marking, final_marking)
    bottlenecks = analyzer.identify_bottlenecks()
    print("Gargalos identificados:")
    for b in bottlenecks:
        print(b)

    sankhya_script = analyzer.generate_sankhya_flow_script(bottlenecks)
    with open("sankhya_flow_script.js", "w") as f:
        f.write(sankhya_script)
    print("Script Sankhya Flow gerado em: sankhya_flow_script.js")



