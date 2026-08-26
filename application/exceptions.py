class ApplicationError(Exception):
    """Erro esperado durante a execução de um caso de uso."""


class InvalidQuoteDataError(ApplicationError):
    """Os dados fornecidos para o orçamento são inválidos."""


class RouteNotFoundError(ApplicationError):
    """Nenhuma rota foi encontrada para os dados informados."""


class RouteSearchError(ApplicationError):
    """Falha ao consultar o serviço responsável pela rota."""


class QuoteCalculationError(ApplicationError):
    """Falha ao processar os dados e calcular o orçamento."""


class QuotePdfGenerationError(ApplicationError):
    """Falha ao gerar o documento PDF do orçamento."""


class InvalidCustomerDataError(ApplicationError):
    """Os dados fornecidos para o cliente são inválidos."""


class CustomerAlreadyExistsError(ApplicationError):
    """Já existe cliente com o CPF ou CNPJ informado."""


class CustomerNotFoundError(ApplicationError):
    """Cliente não encontrado."""


class CustomerPersistenceError(ApplicationError):
    """Falha ao persistir ou consultar dados do cliente."""


class QuoteNotFoundError(ApplicationError):
    """Orçamento não encontrado."""


class QuotePersistenceError(ApplicationError):
    """Falha ao persistir ou consultar orçamento."""


class QuoteNumberGenerationError(ApplicationError):
    """Falha ao gerar número do orçamento."""


class QuotePricingPolicyError(ApplicationError):
    """Falha ao obter a política de precificação."""


class QuoteVersionCalculationError(ApplicationError):
    """Falha ao calcular uma versão do orçamento."""


class InvalidQuoteStateError(ApplicationError):
    """O orçamento não permite a operação no estado atual."""


class QuoteConcurrentModificationError(ApplicationError):
    """O orçamento foi alterado durante a operação."""


class InvalidFreightDataError(ApplicationError):
    """Os dados fornecidos para o frete são inválidos."""


class FreightAlreadyExistsError(ApplicationError):
    """O orçamento principal já possui um frete associado."""


class FreightPersistenceError(ApplicationError):
    """Falha ao persistir ou consultar frete."""


class FreightNotFoundError(ApplicationError):
    """Frete não encontrado."""


class InvalidFreightStateError(ApplicationError):
    """O frete não permite a operação no estado atual."""


class InvalidDriverDataError(ApplicationError):
    """Os dados fornecidos para o motorista são inválidos."""


class DriverAlreadyExistsError(ApplicationError):
    """Já existe motorista com o CPF informado."""


class DriverPersistenceError(ApplicationError):
    """Falha ao persistir ou consultar motorista."""


class DriverNotFoundError(ApplicationError):
    """Motorista não encontrado."""


class InvalidDriverStateError(ApplicationError):
    """O motorista não permite a operação no estado atual."""


class FreightTransportUnitNotFoundError(ApplicationError):
    """Unidade de transporte do frete não encontrada."""


class FreightDriverAssignmentNotFoundError(ApplicationError):
    """Participação de motorista no frete não encontrada."""


class FreightDriverAssignmentPersistenceError(ApplicationError):
    """Falha ao persistir ou consultar participação de motorista."""


class FreightOperationalAssignmentPersistenceError(ApplicationError):
    """Falha ao persistir ou consultar contexto operacional do frete."""


class FreightVehicleRecordPersistenceError(ApplicationError):
    """Falha ao persistir ou consultar veículo operacional do frete."""


class FreightExpensePersistenceError(ApplicationError):
    """Falha ao persistir ou consultar despesa realizada do frete."""


class FreightExpenseNotFoundError(ApplicationError):
    """Despesa realizada do frete não encontrada."""


class FreightFinancialResultPersistenceError(ApplicationError):
    """Falha ao persistir ou consultar fechamento financeiro do frete."""


class InvalidVehicleDataError(ApplicationError):
    """Os dados fornecidos para o veículo são inválidos."""


class VehicleAlreadyExistsError(ApplicationError):
    """Já existe veículo com a placa informada."""


class VehicleNotFoundError(ApplicationError):
    """Veículo não encontrado."""


class VehiclePersistenceError(ApplicationError):
    """Falha ao persistir ou consultar veículo."""


class InvalidTransportProviderDataError(ApplicationError):
    """Os dados fornecidos para o prestador são inválidos."""


class TransportProviderAlreadyExistsError(ApplicationError):
    """Já existe prestador com o documento informado."""


class TransportProviderNotFoundError(ApplicationError):
    """Prestador de transporte não encontrado."""


class InvalidTransportProviderStateError(ApplicationError):
    """O prestador não permite a operação no estado atual."""


class TransportProviderPersistenceError(ApplicationError):
    """Falha ao persistir ou consultar prestador de transporte."""


class TransportProviderAffiliationPersistenceError(ApplicationError):
    """Falha ao persistir ou consultar vínculo do prestador."""
