# -*- coding: utf-8 -*-
"""Consulta SQL do monitoramento de fracionamento (mantida integralmente)."""

SQL_FRACIONAMENTO = """
SELECT * FROM (
    SELECT *, SUM(ValPagar) OVER (PARTITION BY CodForn_Proc) AS ValorTotalFornecedor
    FROM (
        SELECT DISTINCT
            Dados_Proc.Empresa_proc AS [Dados_Proc.Empresa_Proc],
            Dados_Proc.Obra_Proc AS [Dados_Proc.Obra_proc],
            Dados_Proc.Num_Proc AS [Dados_Proc.Num_Proc],
            [NumCot_Proc],
            [OrdemCompra_Proc],
            [Contrato_Proc],
            [CodMed_Proc],
            ISNULL(Parc_proc.EnviadoComoRiscoSacado_proc,0) AS [EnviadoComoRiscoSacado],
            Dados_Proc.User_Proc,
            Dados_Proc.CodForn_Proc,
            Dados_Proc.Data_Proc,
            Dados_Proc.TipoDoc_Proc,
            Dados_Proc.IntExt_Proc,
            Dados_Proc.ObrFiscal_Proc,
            Dados_Proc.Contato_Proc,
            Dados_Proc.EmpPaga_Proc,
            Dados_Proc.EmpFatura_Proc,
            Dados_Proc.CategProc_proc,
            Dados_Proc.Anexos_proc,
            Dados_Proc.NumEnt_Proc,
            Bancos.Nome_banco AS [NomeBanco],
            CCorrente.Descri_banco AS [DescriCCorrente],
            Pessoas.Nome_pes AS [NomeFornecedor],
            Pessoas.Cpf_pes AS [CnpjCpf],
            Pessoas.NomeFant_Pes AS [NomeFantFornecedor],
            Pessoas1.Nome_pes AS [NomeEmp_Paga],
            Pessoas2.Nome_pes AS [NomeEmp_Fatura],
            CategoriasDeMovFin.Desc_cmf,
            Contratos.Situacao_cont,
            Obras.Descr_obr,
            Empresas.Desc_emp,
            DadosProcParam.PorcJuro_ProcPar,
            DadosProcParam.PorcMulta_ProcPar,
            DadosProcParam.TipoJuro_ProcPar,
            DadosProcParam.ReterImposto_ProcPar,
            DadosProcParam.NumCsf_ProcPar,
            DadosProcParam.TipoImposto_ProcPar,
            DadosProcParam.Aliquota_ProcPar,
            DadosProcParam.Protocolo_ProcPar,
            DadosProcParam.Adiantamento_ProcPar,
            DadosProcParam.QtdeParcelas_ProcPar,
            Pessoas3.Nome_pes AS [NomeBeneficiario],
            SequenciaParcelaProcesso.NumSeqParcela_pps,
            TabRelatorio.Obra_RelAdmObr,
            TabRelatorio.descr_obr AS [Desc_Obra_RelAdmObr],
            TabRelatorio.Num_RelAdmObr,
            TabRelatorio.Descricao_RelAdmObr,
            TabRelatorio.Num_nfe,
            CodigoServicoFiscal.Descr_csf,
            CodigoServicoFiscal.CodigoCsrf_csf,
            CodigoServicoFiscal.CodigoNbs_csf,
            DadosProcParam.EmpresaProcPaiReemb_ProcPar,
            TabNBS.Descr_nbs,
            GruposDeObra.Codigo_cger,
            GruposDeObra.Desc_cger,
            ContratoRiscoSacado.Id_crs,
            ContratoRiscoSacado.Descricao_crs,
            Parc_Proc.*,
            ((Parc_Proc.ValorParc_Proc + Parc_Proc.AcrescParc_Proc) - Parc_Proc.DescParc_Proc) AS [ValPagar],
            CASE WHEN ConfEmissao_Proc = 0 THEN '0-Não' WHEN ConfEmissao_Proc = 1 THEN '1-Sim' END AS [Aprovado],
            CAST(? AS DATE) AS [DataInicio],
            CAST(? AS DATE) AS [DataTermino],
            CAST(TributoVincProc.NumTri_tvp AS VARCHAR) + '-' +  CAST(TributoVincProc.TipoTri_tvp AS VARCHAR) AS [ChaveTributo_proc],
            CAST(DataAprovEmissao_proc AS DATE) AS [DtAprovEmissao_proc],
            CONVERT(CHAR(8), DataAprovEmissao_proc, 108) AS [HoraAprovEmissao_proc],
            NULL AS [NomeArquivoPgto_papg],
            NULL AS [StatusArquivo_papg],
            NULL AS [NomeArquivoBaixa_papg],
            NULL AS [OcorrenciaPagamento_papg]
        FROM Dados_Proc
        INNER JOIN [Parc_Proc] AS [Parc_Proc] ON [Dados_Proc].[Empresa_proc] = [Parc_Proc].[Empresa_proc] AND [Dados_Proc].[Num_Proc] = [Parc_Proc].[Num_Proc] AND [Dados_Proc].[Obra_Proc] = [Parc_Proc].[Obra_Proc]
        LEFT JOIN [Notfisc_Proc] AS [Notfisc_Proc] ON [Parc_Proc].[Empresa_proc] = [Notfisc_Proc].[Empresa_proc] AND [Parc_Proc].[Obra_Proc] = [Notfisc_Proc].[Obra_Proc] AND [Parc_Proc].[Num_Proc] = [Notfisc_Proc].[Num_Proc] AND [Parc_Proc].[NumParc_Proc] = [Notfisc_Proc].[NumParc_Proc]
        LEFT JOIN [NotasFiscaisEnt] AS [NotasFiscaisEnt] ON [Notfisc_Proc].[Empresa_proc] = [NotasFiscaisEnt].[Empresa_nfe] AND [Notfisc_Proc].[NumNfe_Proc] = [NotasFiscaisEnt].[Num_nfe]
        LEFT JOIN [CCorrente] AS [CCorrente] ON [Parc_Proc].[Empresa_proc] = [CCorrente].[Empresa_banco] AND [Parc_Proc].[BanContParc_proc] = [CCorrente].[Numero_banco] AND [Parc_Proc].[Conta_Proc] = [CCorrente].[Conta_banco]
        LEFT JOIN [Bancos] AS [Bancos] ON [Parc_Proc].[BanContParc_proc] = [Bancos].[Numero_banco]
        LEFT JOIN [DadosProcParam] AS [DadosProcParam] ON [Dados_Proc].[Empresa_proc] = [DadosProcParam].[Empresa_ProcPar] AND [Dados_Proc].[Num_Proc] = [DadosProcParam].[NumProc_ProcPar] AND [Dados_Proc].[Obra_Proc] = [DadosProcParam].[Obra_ProcPar]
        INNER JOIN [Empresas] AS [Empresas] ON [Dados_Proc].[Empresa_proc] = [Empresas].[Codigo_emp]
        INNER JOIN [Obras] AS [Obras] ON [Dados_Proc].[Obra_Proc] = [Obras].[Cod_obr] AND [Empresas].[Codigo_emp] = [Obras].[Empresa_obr]
        LEFT JOIN [SequenciaParcelaProcesso] AS [SequenciaParcelaProcesso] ON [Parc_Proc].[Empresa_proc] = [SequenciaParcelaProcesso].[Empresa_pps] AND [Parc_Proc].[Obra_Proc] = [SequenciaParcelaProcesso].[Obra_pps] AND [Parc_Proc].[Num_Proc] = [SequenciaParcelaProcesso].[NumProc_pps] AND [Parc_Proc].[NumParc_Proc] = [SequenciaParcelaProcesso].[NumParc_pps]
        LEFT JOIN [Contratos] AS [Contratos] ON [Dados_Proc].[Empresa_proc] = [Contratos].[Empresa_cont] AND [Dados_Proc].[Obra_Proc] = [Contratos].[Obra_cont] AND [Dados_Proc].[Contrato_Proc] = [Contratos].[Cod_cont]
        LEFT JOIN [CategoriasDeMovFin] AS [CategoriasDeMovFin] ON [Parc_Proc].[CategMovFin_Proc] = [CategoriasDeMovFin].[Codigo_cmf]
        LEFT JOIN [Pessoas] AS [Pessoas1] ON [Dados_Proc].[EmpPaga_Proc] = [Pessoas1].[Cod_pes]
        LEFT JOIN [Pessoas] AS [Pessoas2] ON [Dados_Proc].[EmpFatura_Proc] = [Pessoas2].[Cod_pes]
        LEFT JOIN [Pessoas] AS [Pessoas] ON [Dados_Proc].[CodForn_Proc] = [Pessoas].[Cod_pes]
        LEFT JOIN [Pessoas] AS [Pessoas3] ON CodPesNovoBeneficiario_proc = [Pessoas3].[Cod_pes]
        LEFT JOIN [CodigoServicoFiscal] AS [CodigoServicoFiscal] ON [DadosProcParam].[NumCsf_ProcPar] = [CodigoServicoFiscal].[Num_csf]
        LEFT JOIN [TabNBS] AS [TabNBS] ON [CodigoServicoFiscal].[CodigoNbs_csf] = [TabNBS].[Codigo_nbs]
        LEFT JOIN [TributoVincProc] AS [TributoVincProc] ON [Parc_Proc].[Empresa_proc] = [TributoVincProc].[Empresa_tvp] AND [Parc_Proc].[Obra_Proc] = [TributoVincProc].[ObraProc_tvp] AND [Parc_Proc].[Num_Proc] = [TributoVincProc].[NumProc_tvp] AND [Parc_Proc].[NumParc_Proc] = [TributoVincProc].[NumParcProc_tvp]
        LEFT JOIN (
            SELECT DISTINCT COALESCE(RelADM.Descricao_RelAdmObr, RelatorioAdmObra.Descricao_RelAdmObr) AS Descricao_RelAdmObr, COALESCE(RelADM.Num_RelAdmObr, RelatorioAdmObra.Num_RelAdmObr) AS Num_RelAdmObr, COALESCE(RelADM.Obra_RelAdmObr, RelatorioAdmObra.Obra_RelAdmObr) AS Obra_RelAdmObr, COALESCE(obr.descr_obr, Obras.descr_obr) AS descr_obr, NotasFiscaisEnt.Empresa_nfe, NotasFiscaisEnt.Num_nfe, Notfisc_Proc.Num_Proc, Notfisc_Proc.NumParc_Proc, Notfisc_Proc.Obra_Proc, Notfisc_Proc.Empresa_proc
            FROM Notfisc_Proc WITH(NOLOCK) INNER JOIN NotasFiscaisEnt WITH(NOLOCK) ON Notfisc_Proc.Empresa_proc = NotasFiscaisEnt.Empresa_nfe AND Notfisc_Proc.NumNfe_Proc = NotasFiscaisEnt.Num_nfe LEFT JOIN RelatorioAdmObra RelADM WITH(NOLOCK) ON RelADM.Empresa_RelAdmObr = NotasFiscaisEnt.Empresa_nfe AND RelADM.Obra_RelAdmObr = NotasFiscaisEnt.ObraRelAdm_nfe AND RelADM.Num_RelAdmObr = NotasFiscaisEnt.NumRelAdm_nfe LEFT JOIN RelAdmObraProc WITH(NOLOCK) ON RelAdmObraProc.Empresa_RelProc = Notfisc_Proc.Empresa_proc AND RelAdmObraProc.ObraProc_RelProc = Notfisc_Proc.Obra_Proc AND RelAdmObraProc.NumProc_RelProc = Notfisc_Proc.Num_Proc AND RelAdmObraProc.NumParc_RelProc = Notfisc_Proc.NumParc_Proc AND RelAdmObraProc.NumNfe_RelProc = Notfisc_Proc.NumNfe_Proc LEFT JOIN RelatorioAdmObra WITH(NOLOCK) ON RelatorioAdmObra.Empresa_RelAdmObr = RelAdmObraProc.Empresa_RelProc AND RelatorioAdmObra.Obra_RelAdmObr = RelAdmObraProc.ObraRelAdm_RelProc AND RelatorioAdmObra.Num_RelAdmObr = RelAdmObraProc.NumRelAdm_RelProc LEFT JOIN Obras WITH(NOLOCK) ON Obras.Empresa_obr = RelatorioAdmObra.Empresa_RelAdmObr AND Obras.cod_obr = RelatorioAdmObra.Obra_RelAdmObr LEFT JOIN Obras obr WITH(NOLOCK) ON obr.Empresa_obr = RelADM.Empresa_RelAdmObr AND obr.cod_obr = RelADM.Obra_RelAdmObr INNER JOIN Parc_Proc WITH(NOLOCK) ON Notfisc_Proc.Empresa_proc = Parc_Proc.Empresa_proc AND Notfisc_Proc.Num_Proc = Parc_Proc.Num_Proc AND Notfisc_Proc.NumParc_Proc = Parc_Proc.NumParc_Proc AND Notfisc_Proc.Obra_Proc = Parc_Proc.Obra_Proc
            WHERE NOT EXISTS( SELECT * FROM RelAdmObraProcVinc WITH(NOLOCK) WHERE RelAdmObraProcVinc.Empresa_RelProcVinc = Parc_Proc.Empresa_proc AND RelAdmObraProcVinc.ObraProc_RelProcVinc = Parc_Proc.Obra_Proc AND RelAdmObraProcVinc.NumProcVinc_ProcParVinc = Parc_Proc.Num_Proc AND RelAdmObraProcVinc.NumParcProcVinc_ProcParVinc = Parc_Proc.NumParc_Proc )
            UNION
            SELECT DISTINCT Descricao_RelAdmObr, Num_RelAdmObr, Obra_RelAdmObr, descr_obr, NotasFiscaisEnt.Empresa_nfe, NotasFiscaisEnt.Num_nfe, RelAdmObraProcVinc.NumProcVinc_ProcParVinc AS Num_Proc, RelAdmObraProcVinc.NumParcProcVinc_ProcParVinc AS NumParc_Proc, Notfisc_Proc.Obra_Proc, Notfisc_Proc.Empresa_proc
            FROM NotasFiscaisEnt WITH(NOLOCK) INNER JOIN Notfisc_Proc WITH(NOLOCK) ON Notfisc_Proc.Empresa_proc = NotasFiscaisEnt.Empresa_nfe AND Notfisc_Proc.NumNfe_Proc = NotasFiscaisEnt.Num_nfe INNER JOIN RelAdmObraProc WITH(NOLOCK) ON RelAdmObraProc.Empresa_RelProc = Notfisc_Proc.Empresa_proc AND RelAdmObraProc.ObraProc_RelProc = Notfisc_Proc.Obra_Proc AND RelAdmObraProc.NumProc_RelProc = Notfisc_Proc.Num_Proc AND RelAdmObraProc.NumParc_RelProc = Notfisc_Proc.NumParc_Proc AND RelAdmObraProc.NumNfe_RelProc = Notfisc_Proc.NumNfe_Proc INNER JOIN RelatorioAdmObra WITH(NOLOCK) ON RelatorioAdmObra.Empresa_RelAdmObr = RelAdmObraProc.Empresa_RelProc AND RelatorioAdmObra.Obra_RelAdmObr = RelAdmObraProc.ObraRelAdm_RelProc AND RelatorioAdmObra.Num_RelAdmObr = RelAdmObraProc.NumRelAdm_RelProc AND RelatorioAdmObra.TipoTxAdm_RelAdmObr = 1 INNER JOIN Obras WITH(NOLOCK) ON Obras.Empresa_obr = RelatorioAdmObra.Empresa_RelAdmObr AND Obras.cod_obr = RelatorioAdmObra.Obra_RelAdmObr INNER JOIN RelAdmObraProcVinc WITH(NOLOCK) ON RelAdmObraProcVinc.Empresa_RelProcVinc = RelAdmObraProc.Empresa_RelProc AND RelAdmObraProcVinc.ObraProc_RelProcVinc = RelAdmObraProc.ObraProc_RelProc AND RelAdmObraProcVinc.NumProc_RelProcVinc = RelAdmObraProc.NumProc_RelProc AND RelAdmObraProcVinc.NumParc_RelProcVinc = RelAdmObraProc.NumParc_RelProc AND RelAdmObraProcVinc.NumNfe_RelProcVinc = RelAdmObraProc.NumNfe_RelProc AND RelAdmObraProcVinc.ObraRelAdm_RelProcVinc = RelAdmObraProc.ObraRelAdm_RelProc AND RelAdmObraProcVinc.NumRelAdm_RelProcVinc = RelAdmObraProc.NumRelAdm_RelProc
        ) AS [TabRelatorio]
            ON Parc_Proc.Empresa_proc = TabRelatorio.Empresa_proc AND Parc_Proc.Obra_Proc = TabRelatorio.Obra_Proc AND Parc_Proc.Num_Proc = TabRelatorio.Num_Proc AND Parc_Proc.NumParc_Proc = TabRelatorio.NumParc_Proc
        LEFT JOIN (
            SELECT MAX(IdCrs_prs) AS IdCrs_prs, Empresa_prs, Obra_prs, NumProc_prs, NumParc_prs FROM ParcelaRiscoSacado WITH(NOLOCK) WHERE StatusEnvio_prs NOT IN (4, 7) GROUP BY Empresa_prs, Obra_prs, NumProc_prs, NumParc_prs
        ) ParcelaRiscoSacado ON Empresa_prs = Parc_Proc.Empresa_proc AND Obra_prs = Parc_Proc.Obra_Proc AND NumProc_prs = Parc_Proc.Num_Proc AND NumParc_prs = Parc_Proc.NumParc_Proc
        LEFT JOIN ContratoRiscoSacado WITH(NOLOCK) ON Id_crs = IdCrs_prs
        LEFT JOIN GruposDeObra WITH(NOLOCK) ON Codigo_cger = CodGrupo_obr
        WHERE Parc_Proc.StatusParc_proc IN (1,3)
        AND (Obras.status_obr < 1 OR Obras.status_obr = 3)
        AND Parc_Proc.DtPagParc_Proc BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
        AND Parc_Proc.ValorParc_Proc < ?
        AND Pessoas.Cpf_pes NOT LIKE '%19758842000135%' AND Pessoas.Nome_pes NOT LIKE '%APORTE%'
    ) AS Dados_Proc
) AS ResultadoFinal
WHERE ValorTotalFornecedor > ?
ORDER BY ResultadoFinal.CodForn_Proc, DtPagParc_Proc, ChqNome_Proc, Grupo_Proc
"""
