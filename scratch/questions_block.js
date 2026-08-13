{
    start: {
        id: 'start',
        text: 'Você já realiza entregas pelo iFood?',
        options: [
            { text: 'Sim, já sou parceiro', icon: '🛵', next: 'tempo_atividade' },
            { text: 'Ainda não, quero começar', icon: '🚀', next: 'possu_veiculo' }
        ]
    },
    tempo_atividade: {
        id: 'tempo_atividade',
        text: 'Há quanto tempo você está nas entregas?',
        options: [
            { text: 'Estou começando agora', icon: '🌱', next: 'disponibilidade' },
            { text: 'Menos de 1 ano', icon: '⭐', next: 'disponibilidade' },
            { text: 'Mais de 1 ano', icon: '🏆', next: 'disponibilidade' }
        ]
    },
    possu_veiculo: {
        id: 'possu_veiculo',
        text: 'Você já tem veículo para entregas?',
        options: [
            { text: 'Sim, já tenho', icon: '✅', next: 'tipo_veiculo' },
            { text: 'Estou providenciando', icon: '🛠️', next: 'tipo_veiculo' }
        ]
    },
    tipo_veiculo: {
        id: 'tipo_veiculo',
        text: 'Qual será seu principal meio de entrega?',
        options: [
            { text: 'Moto', icon: '🏍️', next: 'cnh_status' },
            { text: 'Bicicleta', icon: '🚲', next: 'disponibilidade' }
        ]
    },
    cnh_status: {
        id: 'cnh_status',
        text: 'Qual é a situação da sua CNH?',
        options: [
            { text: 'EAR (Atividade remunerada)', icon: '✅', next: 'disponibilidade' },
            { text: 'CNH comum (sem EAR)', icon: '⚠️', next: 'disponibilidade' },
            { text: 'Provisória', icon: '🔰', next: 'disponibilidade' }
        ]
    },
    disponibilidade: {
        id: 'disponibilidade',
        text: 'Quantas horas por dia você pretende ficar online?',
        options: [
            { text: 'Até 4 horas', icon: '⏱️', next: 'objetivo_renda' },
            { text: '4 a 8 horas', icon: '💼', next: 'objetivo_renda' },
            { text: 'Mais de 8 horas', icon: '🚀', next: 'objetivo_renda' }
        ]
    },
    objetivo_renda: {
        id: 'objetivo_renda',
        text: 'Qual é seu objetivo com as entregas?',
        options: [
            { text: 'Renda extra', icon: '💡', next: 'regiao_preferencia' },
            { text: 'Renda principal', icon: '📈', next: 'regiao_preferencia' },
            { text: 'Quero crescer rápido', icon: '🔥', next: 'regiao_preferencia' }
        ]
    },
    regiao_preferencia: {
        id: 'regiao_preferencia',
        text: 'Onde você prefere atuar?',
        options: [
            { text: 'Centro e arredores', icon: '🏙️', next: 'equipamento' },
            { text: 'Bairros residenciais', icon: '🏡', next: 'equipamento' },
            { text: 'Próximo a shoppings', icon: '🛍️', next: 'equipamento' }
        ]
    },
    equipamento: {
        id: 'equipamento',
        text: 'Você já tem bag térmica em boas condições?',
        options: [
            { text: 'Sim, mas preciso trocar', icon: '♻️', next: 'horario_pico' },
            { text: 'Não tenho, preciso da primeira', icon: '🎒', next: 'horario_pico' },
            { text: 'Tenho e quero uma reserva', icon: '✅', next: 'horario_pico' }
        ]
    },
    horario_pico: {
        id: 'horario_pico',
        text: 'Você consegue rodar em horários de pico (almoço/jantar)?',
        options: [
            { text: 'Sim, com certeza', icon: '🔥', next: 'personal_step' },
            { text: 'Consigo às vezes', icon: '📅', next: 'personal_step' },
            { text: 'Prefiro horários alternativos', icon: '🌙', next: 'personal_step' }
        ]
    }
};