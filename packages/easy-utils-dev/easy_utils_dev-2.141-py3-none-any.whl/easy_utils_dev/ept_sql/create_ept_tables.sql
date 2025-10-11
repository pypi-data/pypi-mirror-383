BEGIN TRANSACTION;

CREATE TABLE Add4RxOFAParameters (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 NF_IROADM9R_PSC TEXT,
 NF_OTHER TEXT,
 GAIN_TILT_COEFF TEXT,
 OA_RIPPLE TEXT,
 NF_MCS2XL TEXT
);

CREATE TABLE AddDrop (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 schan TEXT,
 dwdm TEXT,
 cwdm TEXT
);


CREATE TABLE BackplaneConnection (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 type TEXT
);

CREATE TABLE Booster (
parentId TEXT,
parentTag TEXT,
parentAttrs TEXT,
grandparentId TEXT,
grandparentTag TEXT,
grandparentAttrs TEXT,
OAtype TEXT,
type TEXT,
height TEXT,
width TEXT,
supervisorygain TEXT,
release TEXT,
pldm TEXT,
pldmInDcmNetwork TEXT,
pldmInNoDcmNetwork TEXT,
insertionloss TEXT,
oppcout TEXT,
oppcout88 TEXT
);

CREATE TABLE CDCAD (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 sequenceID TEXT,
 shelfSetID TEXT,
 cdcad_type TEXT,
 source TEXT,
 year TEXT,
 id TEXT,
 mshShelfIDList TEXT,
 isUserCreated TEXT
);

CREATE TABLE CDCCircuitPack (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 sequenceID TEXT,
 circuitPackID TEXT,
 projectIDs TEXT
);

CREATE TABLE CWRtype (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 type TEXT,
 height TEXT,
 width TEXT,
 gainexcessmax TEXT,
 OHmax TEXT,
 AddAmpType TEXT,
 CDropLoss TEXT,
 CDropLossNom TEXT,
 CDropLossMin TEXT,
 SFDDropLoss TEXT,
 SFDDropLossNom TEXT,
 SFDDropLossMin TEXT,
 ThruOutLoss TEXT,
 ThruOutLossNom TEXT,
 ThruOutLossMin TEXT,
 ThruInLoss TEXT,
 ThruInLossNom TEXT,
 ThruInLossMin TEXT,
 SFDAddLoss TEXT,
 SFDAddLossNom TEXT,
 SFDAddLossMin TEXT,
 CAddLoss TEXT,
 CAddLossNom TEXT,
 CAddLossMin TEXT,
 AmpOutLoss TEXT,
 AmpOutLossNom TEXT,
 AmpOutLossMin TEXT,
 AddChanMax TEXT,
 wtdSigOutMin TEXT,
 PDL TEXT,
 PMD TEXT,
 isAddWR TEXT,
 supportPSC TEXT,
 isFlexSupport TEXT,
 GMPLSSupport TEXT,
 supportedWithDCM TEXT,
 supportPTPIO TEXT,
 supportPTPIOC TEXT,
 WRMeshOutLoss TEXT,
 WRMeshOutLossNom TEXT,
 WRMeshOutLossMin TEXT,
 WRAddInLoss TEXT,
 WRAddInLossNom TEXT,
 WRAddInLossMin TEXT,
 SigOutPortLOS TEXT,
 isSupportedByOMSP TEXT,
 PDL15to10WSSAtt TEXT,
 sigin_mesh_max TEXT,
 sigin_mesh_nom TEXT,
 sigin_mesh_min TEXT,
 mesh_sigout_max TEXT,
 mesh_sigout_nom TEXT,
 mesh_sigout_min TEXT,
 sigin_drop_max TEXT,
 sigin_drop_nom TEXT,
 sigin_drop_min TEXT,
 add_sigout_max TEXT,
 add_sigout_nom TEXT,
 add_sigout_min TEXT,
 numADTPorts TEXT,
 rcvAmp TEXT,
 xmtAmp TEXT,
 feature TEXT
);

CREATE TABLE CentralFrequencyGranularity (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 granularity TEXT
);

CREATE TABLE Channel (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 num TEXT,
 band_portion TEXT,
 name TEXT
);

CREATE TABLE ChannelAssignmentPlan (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 ID TEXT,
 channelplan TEXT,
 release TEXT
);

CREATE TABLE ChannelCapacity (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 capacity TEXT,
 gmpls TEXT,
 excludefromdefaults TEXT,
 release TEXT
);

CREATE TABLE ChannelFormat (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 IETF_G694_1_channel_numbering TEXT
);

CREATE TABLE ChannelPlan (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 ID TEXT,
 chanmin TEXT,
 chanmax TEXT,
 release TEXT
);

CREATE TABLE ClientLine (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 Type TEXT
);

CREATE TABLE CompModuleInterworkingEntry (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 TxCompModule TEXT,
 RxCompModule TEXT,
 Other TEXT,
 OsnrTarget TEXT,
 PMD TEXT,
 FaddClsAdd TEXT,
 CD TEXT,
 GMPLS TEXT,
 TxPluggable TEXT,
 RxOt TEXT,
 TxOt TEXT,
 RxPluggable TEXT
);

CREATE TABLE DCMtype (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 DCMtype TEXT,
 PMD TEXT,
 PDL TEXT,
 disp1528 TEXT,
 disp1528min TEXT,
 disp1528max TEXT,
 disp1546 TEXT,
 disp1546min TEXT,
 disp1546max TEXT,
 disp1565 TEXT,
 disp1565min TEXT,
 disp1565max TEXT,
 loss TEXT,
 minLoss TEXT,
 maxLoss TEXT,
 leff TEXT,
 gamma TEXT,
 fiberLength TEXT,
 height TEXT,
 width TEXT,
 release TEXT,
 FiberType TEXT,
 isLowLatency TEXT
);

CREATE TABLE DGE (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 dgeName TEXT,
 dgeType TEXT,
 isGMPLSSupported TEXT
);

CREATE TABLE DMCoherentUnbandedFiberParams (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 FiberType TEXT,
 dmcu_ExtraPen TEXT,
 alpha_ref TEXT,
 beta_NL TEXT,
 alpha_ref_100GHz TEXT,
 beta_NL_100GHz TEXT
);

CREATE TABLE DMCoherentUnbandedModel (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 dmcu_NLT_penalty TEXT,
 dmcu_fecMargin TEXT,
 dmcu_wc_offset TEXT,
 dmcu_wc_offset_ELEAF TEXT,
 dmcu_wc_offset_100GHz TEXT
);

CREATE TABLE EPTdesign (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE ERROR (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 errID TEXT,
 severity TEXT,
 type TEXT,
 msg TEXT,
 objectID TEXT,
 editID TEXT
);

CREATE TABLE Fibertype (
parentId TEXT,
parentTag TEXT,
parentAttrs TEXT,
grandparentId TEXT,
grandparentTag TEXT,
grandparentAttrs TEXT,
FiberType TEXT,
opsysType TEXT,
commissioningType TEXT,
chanplan TEXT,
maxSpanCount TEXT,
pumpdiff TEXT,
srsA TEXT,
srsB TEXT,
srsC TEXT,
srsL TEXT,
rdps TEXT,
disp TEXT,
sigma1528 TEXT,
sigma1546 TEXT,
sigma1565 TEXT,
value TEXT,
deltaAlpha1625 TEXT,
dispslope TEXT,
dispslopemax TEXT,
dispslopemin TEXT,
gamma TEXT,
gamma_Lband TEXT,
maxphaseshift TEXT,
tiltcoeff TEXT,
tiltcoeff_Lband TEXT,
losscorr1471 TEXT,
losscorr1491 TEXT,
losscorr1511 TEXT,
losscorr1531 TEXT,
losscorr1551 TEXT,
losscorr1571 TEXT,
losscorr1591 TEXT,
losscorr1611 TEXT,
losscorr1310 TEXT,
losscorr1550 TEXT,
dispcorr1471 TEXT,
dispcorr1491 TEXT,
dispcorr1511 TEXT,
dispcorr1531 TEXT,
dispcorr1551 TEXT,
dispcorr1571 TEXT,
dispcorr1591 TEXT,
dispcorr1611 TEXT,
dispcorr1310 TEXT,
dispcorr1550 TEXT,
gmpls TEXT,
supportsAutoPlaceDCMs TEXT,
supportsMixedDCMs TEXT,
ramanGainCoefficient TEXT,
aCoefficient TEXT,
bCoefficient TEXT,
lossConversionFactorFor1510 TEXT,
lossConversionFactorFor1627 TEXT,
release TEXT,
isUserDefFiberType TEXT,
opticalImpairments_CommissioningType TEXT,
CDmid TEXT,
ANLo TEXT,
Alpha TEXT,
Coeff TEXT,
M_QPSK TEXT,
M_BPSK TEXT,
F_QPSK TEXT,
F_BPSK TEXT
);

CREATE TABLE FrequencyRange (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 min TEXT,
 max TEXT,
 band TEXT,
 minFreq TEXT,
 maxFreq TEXT,
 defaultFreq TEXT,
 spinnerMinFreq TEXT,
 spinnerMaxFreq TEXT,
 minChanFixed TEXT,
 maxChanFixed TEXT
);

CREATE TABLE GMPLS (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 encoding TEXT,
 bitrate TEXT,
 compmodule TEXT,
 supportsGMPLSRegen TEXT,
 osnr TEXT,
 osnr_adjust TEXT,
 supportsRestoration TEXT,
 supportsGMPLSRegenInNonControlPlaneAreas TEXT,
 extendedInterWorkingInNonControlPlaneAreas TEXT
);

CREATE TABLE ILAOA (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 OAtype TEXT,
 pldm TEXT,
 pldmInDcmNetwork TEXT,
 pldmInNoDcmNetwork TEXT,
 oppcout TEXT,
 oppcout88 TEXT,
 release TEXT
);

CREATE TABLE ILAtype (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 type TEXT,
 shelfType TEXT,
 release TEXT
);

CREATE TABLE ITLtype (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 type TEXT,
 DropLoss TEXT,
 AddLoss TEXT,
 AddLossMin TEXT,
 height TEXT,
 width TEXT,
 release TEXT
);

CREATE TABLE LBOtype (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 loss TEXT,
 acronym TEXT,
 type TEXT,
 release TEXT
);

CREATE TABLE LineIsolationGroup (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 AllowIsolationGroup TEXT
);

CREATE TABLE LineType (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 type TEXT,
 maxdegree TEXT,
 mindegree TEXT,
 singleFiber TEXT
);

CREATE TABLE MCS (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 type TEXT,
 aarPort TEXT,
 addDropPort TEXT,
 maxDegreSupported TEXT,
 minLoss TEXT,
 nomLoss TEXT,
 maxLoss TEXT,
 pmd TEXT,
 pdl TEXT,
 height TEXT,
 width TEXT,
 release TEXT
);

CREATE TABLE MLFSBSection (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 name TEXT,
 portNameList TEXT
);

CREATE TABLE MLFSBType (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 type TEXT,
 release TEXT,
 lossNom TEXT,
 lossMin TEXT,
 lossMax TEXT
);

CREATE TABLE MONOTDR (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 type TEXT,
 height TEXT,
 width TEXT,
 rxLoss TEXT,
 txLoss TEXT,
 release TEXT
);

CREATE TABLE MSH (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 mapID TEXT,
 mshShelfID TEXT
);

CREATE TABLE MSHShelfMap (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 shelfSetID TEXT,
 bandType TEXT
);

CREATE TABLE MXN (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 type TEXT,
 PDL TEXT,
 PMD TEXT,
 insertionLossMin TEXT,
 insertionLossMax TEXT,
 addDropPort TEXT,
 maxDegreSupported TEXT,
 width TEXT,
 height TEXT,
 release TEXT
);

CREATE TABLE Model1 (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 Qlimit TEXT,
 SNR_Tx TEXT,
 mod1_NLT_penalty TEXT,
 fecMargin TEXT,
 BOL_OsnrMinNom TEXT,
 BOL_OsnrMinWC TEXT,
 BOL_SNR_TX_Nom TEXT,
 BOL_SNR_TX_WC TEXT,
 BOL_QMAX TEXT,
 wlTransPenalty TEXT,
 B0_Linked_OSNRMin TEXT
);

CREATE TABLE Model1FiberParams (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 FiberType TEXT,
 ExtraPen TEXT,
 epsilon TEXT,
 eta TEXT,
 B0 TEXT,
 BOL_epsilon TEXT,
 BOL_B0_50G TEXT,
 B0HighCd TEXT,
 B0_WL_C1 TEXT,
 B0_WL_C2 TEXT,
 B0_WL_C3 TEXT,
 CdThreshold TEXT,
 CdMin TEXT,
 CdMax TEXT,
 B0_CplusL TEXT,
 BOL_B0_50G_CplusL TEXT,
 B0_WL_C1_CplusL TEXT,
 B0_WL_C2_CplusL TEXT,
 B0_WL_C3_CplusL TEXT,
 WL_lowCD TEXT,
 B0_lowCD TEXT,
 B0_lowCD_CplusL TEXT
);

CREATE TABLE MultiChannelService (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 count TEXT,
 contiguous TEXT,
 allowInterweave TEXT,
 spacing TEXT
);

CREATE TABLE NRD (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 FiberType TEXT,
 freq TEXT,
 NRD_min_c0 TEXT,
 NRD_nom_c0 TEXT,
 NRD_max_c0 TEXT,
 NRD_min_c1 TEXT,
 NRD_nom_c1 TEXT,
 NRD_max_c1 TEXT
);

CREATE TABLE NodeConfigADx_MLFSB (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE NodeConfigCDCF (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 MinCDCFADBlockPerOpticalNode TEXT,
 MaxCDCFADBlockPerOpticalNode TEXT,
 MinAARcardsPerMCSadBlock TEXT
);

CREATE TABLE NodeConfigFSx_MLFSB (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 reserveMLFSBAndPSCPerLine TEXT
);

CREATE TABLE NodeConfig_MXN (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 minAscSection TEXT
);

CREATE TABLE OABandCombinations (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE OAPair (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 oaNameC TEXT,
 oaNameL TEXT
);

CREATE TABLE OASectionDetail (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 sectionName TEXT,
 maxPortSectionNumber TEXT
);

CREATE TABLE OAtype (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 OAtype TEXT,
 pldm TEXT,
 opsys TEXT,
 wtocmOK TEXT,
 preampOK TEXT,
 boosterOK TEXT,
 isMonOTDRsupported TEXT,
 release TEXT,
 height TEXT,
 width TEXT,
 isrxoa TEXT,
 canDisableAPR TEXT,
 allowERulesAdjustments TEXT,
 attenuatorWhenNoDCM TEXT,
 isPTPIOCSupported TEXT,
 hasExternalOSCSFPPort TEXT,
 userCanSetMaximumGain TEXT,
 oscSupportRestriction TEXT,
 wtKeysRestriction TEXT,
 isUnidirectional TEXT,
 requireLowLatencyMidStageDCM TEXT,
 isMonOCMsupported TEXT,
 isHybridOA TEXT,
 hybridPreampOAType TEXT,
 hybridPreampVOAMin TEXT,
 hybridPreampVOAMax TEXT,
 hybridPreampVOAInsertionLoss TEXT,
 attenuatorKit TEXT,
 maxDCMLoss TEXT,
 packName TEXT,
 supportedOTDRList TEXT,
 lowPowerVariant TEXT,
 isSwitchedGainOA TEXT,
 is37p5Supported TEXT,
 GMPLSSupported TEXT,
 supportWDMLine TEXT,
 minAARPerMCSADBlock TEXT,
 minMCSPerMCSADBlock TEXT,
 maxMCSPerMCSADBlock TEXT,
 hasIntegratedWTOCMF TEXT,
 isPTPIOSupported TEXT,
 excludeFromOaMap TEXT,
 isOMDCLSupported TEXT
);

CREATE TABLE OMD (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 type TEXT,
 height TEXT,
 width TEXT,
 C_band_combiner_loss_min TEXT,
 C_band_combiner_loss_nom TEXT,
 C_band_combiner_loss_max TEXT,
 C_band_splitter_loss_min TEXT,
 C_band_splitter_loss_nom TEXT,
 C_band_splitter_loss_max TEXT,
 L_band_combiner_loss_min TEXT,
 L_band_combiner_loss_nom TEXT,
 L_band_combiner_loss_max TEXT,
 L_band_splitter_loss_min TEXT,
 L_band_splitter_loss_nom TEXT,
 L_band_splitter_loss_max TEXT,
 Supervisory_add_loss_min TEXT,
 Supervisory_add_loss_max TEXT,
 Supervisory_drop_loss_min TEXT,
 Supervisory_drop_loss_max TEXT,
 PDL TEXT,
 Splitter_isolation TEXT,
 Combiner_isolation TEXT,
 lineInAvailable TEXT,
 release TEXT
);

CREATE TABLE OPStype (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 OPStype TEXT,
 SWLoss TEXT,
 SPLoss TEXT,
 wtdSiginMin TEXT,
 wtdSiginMax TEXT,
 height TEXT,
 width TEXT
);

CREATE TABLE OTtype (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 OTtype TEXT,
 band TEXT,
 otKind TEXT,
 OTheight TEXT,
 OTwidth TEXT,
 ot TEXT,
 fec TEXT,
 mode TEXT,
 PhaseEncoding TEXT,
 coherentBandingRule TEXT,
 isMux TEXT,
 OSNRmin TEXT,
 OSNRmin_config TEXT,
 OSNR_OPSYS_OFFSET TEXT,
 LineSignal TEXT,
 MinPwrOffsetLowerBound TEXT,
 MinPwrOSNROffset TEXT,
 MinOSNRAsymptote TEXT,
 MinPwrAsymptote TEXT,
 OSNRShapeExponent TEXT,
 NoPenaltyDGD TEXT,
 CWR8_cascade_penalty_c1 TEXT,
 CWR8_cascade_penalty_c2 TEXT,
 CWR8_88_cascade_penalty_c1 TEXT,
 CWR8_88_cascade_penalty_c2 TEXT,
 SFD4penalty_c1 TEXT,
 SFD4penalty_c2 TEXT,
 SFD5penalty_c1 TEXT,
 SFD5penalty_c2 TEXT,
 SFD8penalty_c1 TEXT,
 SFD8penalty_maxcount TEXT,
 SFD44penalty_c1 TEXT,
 SFD44penalty_c2 TEXT,
 ILpenalty_c1 TEXT,
 ILpenalty_c2 TEXT,
 ILpenalty_maxcount TEXT,
 TOADMxtalk_penalty_c1 TEXT,
 TOADMxtalk_penalty_c2 TEXT,
 TOADMxtalk_penalty_c3 TEXT,
 TOADMxtalk_penalty_c4 TEXT,
 SFD8xtalk_penalty_c1 TEXT,
 SFD8xtalk_maxcount TEXT,
 ILxtalk_penalty_c1 TEXT,
 FilterIRDM32 TEXT,
 FlickerIRDM32 TEXT,
 Xtalk_IRDM32_1 TEXT,
 Xtalk_IRDM32_2 TEXT,
 FilterIR9 TEXT,
 FlickerIR9 TEXT,
 Trans_penalty_c0 TEXT,
 Trans_penalty_c1 TEXT,
 Trans_penalty_c2 TEXT,
 Trans_penalty_c3 TEXT,
 pwroutmin TEXT,
 pwrinmax TEXT,
 pwrinmin TEXT,
 DGD_max TEXT,
 DGD_penalty_c1 TEXT,
 DGD_penalty_c2 TEXT,
 DGD_penalty_c3 TEXT,
 PDL_penalty_1 TEXT,
 PDL_penalty_2 TEXT,
 PDL_penalty_3 TEXT,
 rcvPwrValidation TEXT,
 aliasing_penalty TEXT,
 dcmRule TEXT,
 supportsMixedDCMs TEXT,
 VirtPreCompDev1 TEXT,
 VirtPreCompDev2 TEXT,
 VirtPreCompDev3 TEXT,
 VirtPreCompDev4p TEXT,
 XPM_Penalty_1 TEXT,
 XPM_Penalty_2 TEXT,
 XPM_Penalty_3 TEXT,
 XPM_Penalty_4 TEXT,
 XPM_Penalty_5 TEXT,
 XPM_Penalty_6 TEXT,
 longspan TEXT,
 supportMultiFec TEXT,
 PhaseEncodingDependByFEC TEXT,
 allowROADM TEXT,
 allowTOADM_CLS TEXT,
 allowAddDrop_CLS TEXT,
 isFlex TEXT,
 pathAdjacency TEXT,
 useMultiDir TEXT,
 NumLinePorts TEXT,
 NumClientPorts TEXT,
 gmpls TEXT,
 canAggregate TEXT,
 route44only TEXT,
 perPortEncryption TEXT,
 routeEven TEXT,
 cwrAdjacencyAllowed TEXT,
 prohibitFiber TEXT,
 allowPSC TEXT,
 allowMCS TEXT,
 useTunableXFP TEXT,
 useTunableZeroChirpXFP TEXT,
 supportAmplifiedLinkDWDM TEXT,
 VOAPortRequired TEXT,
 isUserDefAlienOT TEXT,
 isUserDefFutureOT TEXT,
 isAlienProfileOT TEXT,
 allowSFD48 TEXT,
 allowSFD64 TEXT,
 allowERulesAdjustments TEXT,
 channelType TEXT,
 dspType TEXT,
 allowAddDrop TEXT,
 allowAddDropWithMixingAmplifiedOTUsage TEXT,
 allowAddDropBlock TEXT,
 bandwidth TEXT,
 granularity TEXT,
 supportsOPSFLEX TEXT,
 supportsOPSUM TEXT,
 supportsOPSUMinGMPLS TEXT,
 supportsOptimization TEXT,
 allow1830LX TEXT,
 recoloring TEXT,
 supportsService TEXT,
 useNonLinearSFDFilterPenaltyCalc TEXT,
 WR8_SFD TEXT,
 WR20_SFD TEXT,
 IRDM32_SFD TEXT,
 IR9_SFD TEXT,
 WR8_SFD48 TEXT,
 WR20_SFD48 TEXT,
 IR9_SFD48 TEXT,
 WR8_SFD64 TEXT,
 WR20_SFD64 TEXT,
 IR9_SFD64 TEXT,
 PSC_CF_fAdd TEXT,
 MXN_ASC_fAdd TEXT,
 LOCAL_SFD48_fAdd TEXT,
 LOCAL_SFD64_fAdd TEXT,
 PSC_CF_fDrop TEXT,
 MXN_ASC_fDrop TEXT,
 LOCAL_SFD48_fDrop TEXT,
 LOCAL_SFD64_fDrop TEXT,
 amplifiedASEClass TEXT,
 matchesAmplifiedOTUsage TEXT,
 pwrinmin_unamp TEXT,
 supportsSVOA TEXT,
 supportsFVOA TEXT,
 NumEVOAPorts TEXT,
 fvoaWTKeysRestriction TEXT,
 LinePortPluggable TEXT,
 voa TEXT,
 Qlimit TEXT,
 k1 TEXT,
 k2 TEXT,
 NumBackplanePorts TEXT,
 OTUType TEXT,
 evoaRequired TEXT,
 pwroutmax TEXT,
 node TEXT,
 WSS_88_cascade_maxcount TEXT,
 WSS_20_cascade_maxcount TEXT,
 wtKeysRestriction TEXT,
 filterPenaltyEndpointOverride TEXT,
 WR20_filterless_DGE_penalty TEXT,
 baudRate TEXT,
 NLT_penalty TEXT,
 BtB_a TEXT,
 BtB_b TEXT,
 noITL_OSNRpenalty TEXT,
 WSS_IR9_cascade_maxcount TEXT,
 WR20_xtalk_penalty TEXT,
 WR20_cascade_penalty TEXT,
 SFD_cascade_maxcount TEXT,
 colorless_add_penalty TEXT,
 TX_OSNR TEXT,
 WSS_20_cascade_maxcount_SFD TEXT,
 WSS_IR9_maxcount_SFD TEXT,
 WSS_88_cascade_maxcount_SFD TEXT,
 WSS_WR8_maxcount_SFD48 TEXT,
 WSS_WR20_maxcount_SFD48 TEXT,
 WSS_IR9_maxcount_SFD48 TEXT,
 SFD48_maxcount TEXT,
 WSS_WR8_maxcount_SFD64 TEXT,
 WSS_WR20_maxcount_SFD64 TEXT,
 WSS_IR9_maxcount_SFD64 TEXT,
 SFD64_maxcount TEXT,
 isPTPCTL TEXT,
 maxvoapwrlimit TEXT,
 max_ISR TEXT,
 IROADM_PSC_dropPenalty_a1 TEXT,
 IROADM_PSC_dropPenalty_b1 TEXT,
 IROADM_PSC_dropPenalty_a2 TEXT,
 IROADM_PSC_dropPenalty_b2 TEXT,
 OTSIgModel TEXT,
 pwroutmin_unamp TEXT,
 intwrkmode TEXT,
 profileID TEXT,
 pwrinmax_total TEXT,
 NF TEXT,
 supportedAPN TEXT
);

CREATE TABLE PSCSection (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 name TEXT,
 maxPortSectionNumber TEXT
);

CREATE TABLE PSCType (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 type TEXT,
 PDL TEXT,
 PMD TEXT,
 lossNom TEXT,
 lossMin TEXT,
 lossMax TEXT,
 height TEXT,
 width TEXT,
 release TEXT
);

CREATE TABLE PTPCTL (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 type TEXT,
 numClientPorts TEXT,
 height TEXT,
 width TEXT,
 release TEXT
);

CREATE TABLE PTPIO (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 type TEXT,
 numClientWorkPorts TEXT,
 numClientProtPorts TEXT,
 numLinePorts TEXT,
 hasControl TEXT,
 lossLineInSigOut TEXT,
 lossSigInLineOut TEXT,
 loss1625Drop TEXT,
 loss1625Add TEXT,
 pathLossMin TEXT,
 pathLossMax TEXT,
 dispMax TEXT,
 height TEXT,
 width TEXT,
 release TEXT
);

CREATE TABLE Pluggables (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 clientPortPluggableType TEXT
);

CREATE TABLE PowerFilter (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 PowerFilterType TEXT,
 allowPF30 TEXT,
 allowPF60 TEXT,
 allowPF70 TEXT,
 allowPF20 TEXT,
 allowPF50 TEXT,
 allowPSS16PF20 TEXT,
 allowPSS16PF35 TEXT,
 allowPSS4PF7 TEXT,
 allowPSS4PF4 TEXT,
 allowPSS4PF5 TEXT,
 PSS8PfProt TEXT,
 PSS16PfProt TEXT,
 PSS16IIPfProt TEXT,
 PSS4PfProt TEXT,
 shelfPowerFeedLimit TEXT,
 shelfPowerMargin TEXT,
 shelfVoltageFloor TEXT,
 PSS8PowerFilter TEXT,
 PSS16IIPowerFilter TEXT,
 PSIMPowerFilter TEXT,
 PSI8LPowerFilter TEXT,
 PSI4LPowerFilter TEXT,
 PSIACPowerCord TEXT
);

CREATE TABLE PowerOffset (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 powerOffsetBandwidth TEXT
);


CREATE TABLE Preamp (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,

 preamp TEXT,
 preamploss TEXT,
 preampconnectorloss TEXT,
 preampVOA TEXT
 OAtype TEXT,
 pldm TEXT,
 pldmInDcmNetwork TEXT,
 pldmInNoDcmNetwork TEXT,
 insertionloss TEXT,
 allowedBoosterList TEXT,
 allowedRcvOAColonXmtOAsList TEXT,
 release TEXT
);

CREATE TABLE ROADMPreferences (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 maxAddDropDegree TEXT,
 allowUniDirAddDrop TEXT,
 equipAllMESH4 TEXT,
 equipAllAnyDirADFilter TEXT,
 anyADBlockType TEXT,
 anyDirADBlockOnROADM TEXT,
 WTOCMonXmtOnlyConfigD TEXT,
 maxCWRinADBlock TEXT,
 equipCWRinADBlock TEXT,
 MaxPSCSectionsPerOpticalLine TEXT,
 MinPSCPortPerOpticalLine TEXT,
 MaxPSCSectionsPerADBlock TEXT,
 MinPSCSectionPerADBlock TEXT,
 mlfsb_forceEndTerminalNode TEXT,
 allowHeterogeneousNode TEXT
);

CREATE TABLE ROADMtype (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 type TEXT,
 shelfType TEXT,
 release TEXT
);

CREATE TABLE RcvOA (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 position TEXT,
 role TEXT,
 rxPreserve TEXT,
 OAtype TEXT,
 pldm TEXT,
 pldmInDcmNetwork TEXT,
 pldmInNoDcmNetwork TEXT,
 oppcout TEXT,
 oppcout88 TEXT,
 allowedOtherOAList TEXT,
 supportedOnWR TEXT,
 allowedOtherLineXmt TEXT,
 allowedOtherLineRcv TEXT
);

CREATE TABLE RcvSection (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE Restriction (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 forType TEXT
);

CREATE TABLE RoleDef (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 role TEXT
);

CREATE TABLE SFCtype (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 type TEXT,
 height TEXT,
 width TEXT,
 release TEXT
);

CREATE TABLE SFDtype (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 type TEXT,
 PDL TEXT,
 PMD TEXT,
 height TEXT,
 width TEXT,
 release TEXT
);

CREATE TABLE SegregationInfo (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 noiseLevel TEXT
);


CREATE TABLE SequenceIDSection (
parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 bandType TEXT,
 lineSequenceID TEXT
);

CREATE TABLE ShelfEquipage (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 FiberStorageTray TEXT,
 MixPSI TEXT,
 AttenuatorDrawer TEXT,
 FlexShelf TEXT,
 ShelfCover TEXT,
 ExtShelfCover TEXT,
 RackFill TEXT,
 LinesideXFP TEXT,
 LinesideAttenuator TEXT,
 PSS32FanCapacity TEXT,
 packPlacementSpec TEXT,
 regen TEXT,
 OT260SCX2_OperatingMode TEXT,
 OT1UD200_OperatingMode TEXT,
 SharePSCamongWdmLines TEXT,
 AllowPSS8_UserPanel TEXT,
 PSS32ShelfDepth TEXT,
 installationKit TEXT
);

CREATE TABLE ShelfSetBandDetailConfig (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 bandtype TEXT,
 policyCDCADBlockCreation TEXT,
 allowFSxCreation TEXT
);

CREATE TABLE SingleFiberFilter (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 type TEXT,
 red_insertion_loss_min TEXT,
 red_insertion_loss_nom TEXT,
 red_insertion_loss_max TEXT,
 blue_insertion_loss_min TEXT,
 blue_insertion_loss_nom TEXT,
 blue_insertion_loss_max TEXT,
 red_min_freq TEXT,
 red_max_freq TEXT,
 blue_min_freq TEXT,
 blue_max_freq TEXT
);

CREATE TABLE SiteBandDetailConfig (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 bandtype TEXT,
 DEFAULT_WR TEXT,
 allowFSxCreation TEXT,
 DEFAULT_DGEType TEXT,
 policyCDCADBlockCreation TEXT
);

CREATE TABLE SiteConfigADxMLFSB (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 MinMLFSBSection TEXT,
 MinPSCSection TEXT
);

CREATE TABLE SiteConfigADxMXN (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 minMxNADBlockPerOpticalNode TEXT,
 typeForMxNadBlock TEXT,
 typeForASCadBlock TEXT,
 minASCSections TEXT
);

CREATE TABLE SiteConfigCDCF (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 CdcfCustomSequence TEXT,
 MinCDCFADBlockPerOpticalNode TEXT,
 MaxCDCFADBlockPerOpticalNode TEXT,
 MinAARcardsPerMCSadBlock TEXT,
 AARType TEXT,
 MinMCScardsPerMCSadBlock TEXT,
 MCSType TEXT
);

CREATE TABLE SiteConfigFSxMLFSB (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 MinMLFSBSection TEXT,
 MinPSCSection TEXT,
 reserveMLFSBSectionPerLine TEXT
);

CREATE TABLE TrailList (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE Trans_NPS (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 FiberType TEXT,
 value TEXT,
 spacing TEXT,
 NLT0 TEXT,
 epsilon TEXT,
 extraPen_Banded TEXT,
 highestChan TEXT,
 guardBandWidth TEXT,
 extraGuardBand_DMA TEXT
);

CREATE TABLE Upload (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE UpstreamPack (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 oadmType TEXT,
 wtKeysRestriction TEXT,
 pack TEXT
);

CREATE TABLE VAC (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 type TEXT,
 AddLoss TEXT,
 DropLoss TEXT,
 height TEXT,
 width TEXT
);

CREATE TABLE XmtOA (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 position TEXT,
 role TEXT,
 txPreserve TEXT,
 OAtype TEXT,
 pldm TEXT,
 pldmInDcmNetwork TEXT,
 pldmInNoDcmNetwork TEXT,
 oppcin TEXT,
 oppcout TEXT,
 oppcout88 TEXT,
 allowedOtherOAList TEXT,
 supportedOnWR TEXT
);

CREATE TABLE XmtSection (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE actualTiltPort (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE actualTiltPortL (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE admcolorprofile (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 id TEXT,
 name TEXT,
 value TEXT
);

CREATE TABLE admcolorprofiles (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE alienprofiles (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE allowedDeltaGainPort (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE allowedDeltaGainPortL (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE anssiShelfTypeConfig (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 anssiMainShelfType TEXT
);

CREATE TABLE backclientinterface (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 portnumber TEXT,
 client TEXT,
 pluginterface TEXT,
 Lineport TEXT,
 protection TEXT,
 maxMapping TEXT
);

CREATE TABLE bandDetail (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 bandType TEXT,
 target TEXT,
 pwroutmax TEXT,
 MSLoss TEXT,
 Gboost TEXT,
 PDG TEXT,
 PMD TEXT,
 PDL TEXT,
 tiltprovmin TEXT,
 tiltprovmax TEXT,
 Pdiss TEXT,
 maxppcout TEXT,
 ReverseLoss TEXT,
 ForwardLoss TEXT,
 ReverseLossNom TEXT,
 ReverseLossMin TEXT,
 ForwardLossNom TEXT,
 ForwardLossMin TEXT,
 wtocmLineOutMin TEXT,
 wtocmLineOutMax TEXT,
 wtocmLineOSNRMin TEXT,
 wtocmLineOSNRMax TEXT,
 wtocmRcvOutMin TEXT,
 wtocmRcvOutMax TEXT,
 wtocmRcvOSNRMin TEXT,
 wtocmRcvOSNRMax TEXT,
 wtdLineOutMin TEXT,
 wtdLineOutMax TEXT,
 wtdRcvOutMin TEXT,
 wtdRcvOutMax TEXT,
 redCoeffForRipple TEXT,
 blueCoeffForRipple TEXT,
 opsysRamanPump TEXT,
 oamGainType TEXT,
 hasVOA TEXT,
 voaIntrinsicLoss TEXT,
 voaAffectsOscLoss TEXT,
 minVoaLoss TEXT,
 maxVoaLoss TEXT,
 defaultVoaLoss TEXT,
 limitPositiveTilt TEXT,
 flatGainTilt TEXT,
 offsetGainMaxByDCMLoss TEXT,
 offsetGainMaxFlatByDCMLoss TEXT,
 monOcmLineOutMin TEXT,
 monOcmLineOutMax TEXT,
 monOcmRcvOutMin TEXT,
 monOcmRcvOutMax TEXT,
 wtBeforeVOA TEXT,
 LOSLINEpwroutmin TEXT,
 LOSBeforeVOA TEXT
);

CREATE TABLE bucket (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 lowestChannel TEXT,
 highestChannel TEXT,
 type TEXT
);

CREATE TABLE c_dirs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    SOURCESITE TEXT,
    SOURCEPACKID TEXT,
    SPANID TEXT,
    SOURCEAPN TEXT,
    SOURCEPACKIDREF TEXT,
    DESTINATIONSITE TEXT,
    SOURCEBOARD TEXT,
    SOURCEPHYSICALSLOT TEXT,
    FULLSLOT TEXT,
    SHELFTYPE TEXT
);

CREATE TABLE c_tmp_site_view (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 source TEXT,
 id TEXT,
 name TEXT,
 currentProject TEXT,
 isDeployed TEXT,
 year TEXT,
 allowWDM TEXT,
 etr TEXT,
 clustered TEXT,
 AnssiQSconfigured TEXT,
 EncryptedECneeded TEXT,
 allowPacket TEXT,
 maxOADMDegree TEXT,
 oadmchoice TEXT,
 lineIsolation TEXT,
 lineIsolationOnWTOCM TEXT,
 pduType TEXT,
 pduNumberOfSiteJumperKits TEXT,
 pduIncludeSliderKit TEXT,
 pduIncludeBreakerToggle TEXT,
 PSS16II_AC_POWER TEXT,
 PSS16II_ILAFanCapacity TEXT,
 includeRacks TEXT,
 shelfWidthPSS TEXT,
 shelfWidthPSIM TEXT,
 shelfWidthPSIL TEXT,
 shelfWidthPSI2T TEXT,
 RUVerticalSpacePSS TEXT,
 RUVerticalSpacePSIM TEXT,
 RUVerticalSpacePSIL TEXT,
 RUVerticalSpacePSI2T TEXT,
 passthruoptions TEXT,
 opsyspassthruoptions TEXT,
 RequireROADM TEXT,
 core TEXT,
 ForceSFD44 TEXT,
 WTOCMonILA TEXT,
 Segregation_OT TEXT,
 useLowLatencyDCMsInNonModularOAs TEXT,
 pss8cntrlprot TEXT,
 pss16cntrlprot TEXT,
 pss16IIcntrlprot TEXT,
 pss32cntrlprot TEXT,
 psi8Lcntrlprot TEXT,
 psi4Lcntrlprot TEXT,
 psimcntrlprot TEXT,
 OTDR_in_separate_shelf TEXT,
 OT_in_separate_shelf_for_CDCF TEXT,
 OT_in_separate_shelf TEXT,
 MCS_in_separate_shelf TEXT,
 lat TEXT,
 long TEXT,
 lockLatLong TEXT,
 xcoord TEXT,
 ycoord TEXT,
 FloorAndRoom TEXT,
 maxAislesPerRoom TEXT,
 maxBaysPerAisle TEXT,
 NERegenMode TEXT,
 description TEXT
);

CREATE TABLE changroup (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 chanmin TEXT,
 chanmax TEXT
);

CREATE TABLE chanplan (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 planid TEXT
);

CREATE TABLE circuitpack (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 id TEXT,
 type TEXT,
 apn TEXT,
 manualapn TEXT,
 slotid TEXT,
 wdmline TEXT,
 shelfset TEXT,
 packIDRef TEXT,
 year TEXT,
 dcmpseudoshelf TEXT,
 direction TEXT,
 dcmPlacement TEXT,
 virtual TEXT,
 manualPlacment TEXT,
 opsPackConnected TEXT
);

CREATE TABLE client (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 id TEXT
);

CREATE TABLE coeff (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 fibertype TEXT,
 type TEXT,
 b0 TEXT,
 b1 TEXT,
 b2 TEXT,
 b3 TEXT,
 b4 TEXT,
 b5 TEXT,
 power TEXT,
 b0At1627 TEXT,
 b1At1627 TEXT,
 b2At1627 TEXT,
 b3At1627 TEXT,
 b4At1627 TEXT,
 b5At1627 TEXT
);

CREATE TABLE commonpack (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 id TEXT,
 type TEXT,
 apn TEXT,
 physicalslot TEXT,
 year TEXT,
 manualapn TEXT
);

CREATE TABLE cwr (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 source TEXT,
 id TEXT,
 year TEXT,
 type TEXT,
 CWRpower TEXT,
 AddPPCMin TEXT,
 AddChanMax TEXT,
 packIDRef TEXT
);

CREATE TABLE cwrBandDetail (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 bandType TEXT,
 WSSOH TEXT
);

CREATE TABLE dcmDetail (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 preStage TEXT,
 midStage TEXT,
 postStage TEXT
);

CREATE TABLE dcmDetails (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 isMidStageAllowed TEXT,
 isRcvPreStageAllowed TEXT,
 isXmtPostStageAllowed TEXT,
 isXmtPreStageAllowed TEXT,
 isRcvPostStageAllowed TEXT
);

CREATE TABLE SequenceIDDetail ( 
 parentId TEXT ,
 parentTag TEXT ,
 parentAttrs TEXT ,
 grandparentId TEXT ,
 grandparentTag TEXT ,
 grandparentAttrs TEXT ,
 bandType TEXT ,
 lineSequenceID TEXT 
);

CREATE TABLE demandlist (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE dest (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 id TEXT,
 prot TEXT,
 disjointProt TEXT,
 primshelfset TEXT,
 otPlacement TEXT,
 primsite TEXT,
 primnetype TEXT,
 primlayer TEXT,
 primOT TEXT,
 routingOT TEXT,
 primOTLinePort TEXT,
 primLinePortPlug TEXT,
 backlayer TEXT,
 sharePrimOT TEXT,
 primeAddDropConfig TEXT,
 primeMultiDirAllowed TEXT,
 backAddDropConfig TEXT,
 backMultiDirAllowed TEXT,
 year TEXT,
 encryptOT TEXT,
 encryptOTClientPort TEXT,
 ActualAddDropConfig TEXT,
 type TEXT,
 pluggableOTType TEXT,
 DeliveredOSNR TEXT,
 shelfset TEXT,
 ssdetails TEXT,
 RequiredOSNR TEXT,
 DeliveredPwr TEXT,
 MinDeliveredPwr TEXT,
 MinDeliveredOSNR TEXT,
 ResDisp1528 TEXT,
 ResDisp1546 TEXT,
 ResDisp1565 TEXT,
 NLP TEXT,
 PMD TEXT,
 PDL TEXT,
 XPM TEXT,
 qFactor TEXT,
 pre_fec_ber TEXT,
 weighted_filter_count TEXT,
 DeliveredOSNR_feasibility TEXT,
 RequiredOSNR_feasibility TEXT,
 NLP_feasibility TEXT,
 PMDPenalty_feasibility TEXT,
 PMD_feasibility TEXT,
 PDL_feasibility TEXT,
 PassThruPenalty_feasibility TEXT,
 ChannelMargin_feasibility TEXT,
 isDropLBOApplicable TEXT,
 isDropLBOUserDefined TEXT,
 isAddLBOApplicable TEXT,
 isAddLBOUserDefined TEXT,
 otNE TEXT,
 addLBO TEXT,
 backshelfset TEXT,
 backsite TEXT,
 backnetype TEXT,
 backOT TEXT,
 backOTLinePort TEXT,
 shareBackOT TEXT,
 AddDropConfig TEXT,
 AARType TEXT,
 ADBType TEXT,
 aseNoiseClass TEXT,
 RegenReason TEXT
);

CREATE TABLE eptRegen (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 id TEXT,
 name TEXT,
 ss_A TEXT,
 ss_B TEXT,
 otname TEXT,
 channel_A TEXT,
 channel_B TEXT,
 circuitPackA TEXT,
 circuitPackPortA TEXT,
 circuitPackB TEXT,
 circuitPackPortB TEXT,
 isSfd_A TEXT,
 isSfd_B TEXT,
 isNominal3R TEXT,
 isRestor3R TEXT,
 adblock_idxA TEXT,
 adblock_idxB TEXT,
 FecPort_A TEXT,
 FecPort_B TEXT,
 adblock_cfgA TEXT,
 adblock_cfgB TEXT,
 WDMLink_A TEXT,
 WDMLink_B TEXT,
 isUserCreated TEXT
);

CREATE TABLE failurescope (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 scope TEXT
);

CREATE TABLE feasibility (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 band TEXT,
 bitrate TEXT,
 encoding TEXT,
 PhaseEncoding TEXT,
 compmodule TEXT,
 fec TEXT,
 osnr_mm TEXT,
 osnr_mp TEXT,
 nps_mm TEXT,
 nps_mp TEXT,
 dispersion TEXT,
 dispersion1546 TEXT,
 p_eq_k TEXT,
 mindroppower TEXT
);

CREATE TABLE fiber (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 fibertype TEXT,
 supvgainA TEXT,
 supvgainB TEXT,
 nfA TEXT,
 nfB TEXT,
 power TEXT,
 nfC TEXT,
 rippleA TEXT,
 rippleB TEXT,
 maxNetGain TEXT,
 supvgainA1627 TEXT,
 supvgainB1627 TEXT
);

CREATE TABLE frequencyBucketList (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 bandType TEXT
);

CREATE TABLE gainNotUsedPort (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE gainPort (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE gainPortL (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE gainSetting (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 gainMode TEXT,
 gainminflat TEXT,
 gainmaxflat TEXT,
 gainmin TEXT,
 gainmax TEXT,
 pwrinmin TEXT,
 pwrinmax TEXT,
 pwroutmin TEXT,
 linrip TEXT,
 randrip TEXT,
 TiltToLinRipCoeff TEXT,
 NFc0 TEXT,
 NFc1 TEXT,
 NFc2 TEXT,
 NFc3 TEXT,
 NFc4 TEXT,
 BOL_NFc0 TEXT,
 BOL_NFc1 TEXT,
 BOL_NFc2 TEXT,
 BOL_NFc3 TEXT,
 BOL_NFc4 TEXT,
 ExcessGainToTiltCoeff TEXT,
 TiltToNFCoeff TEXT,
 BOL_TiltToNFCoeff TEXT,
 opsysName TEXT,
 moduleName TEXT,
 supportedIPreAmpXmtCombinations TEXT,
 supportedIPreAmpRcvCombinations TEXT,
 supportedIPreAmpILACombinations TEXT,
 supportedIPreAmpRcvCombinationsWithDCMs TEXT,
 supportedIPreAmpILACombinationsWithDCMs TEXT,
 TiltToNFCoeffPos TEXT,
 BOL_TiltToNFCoeffPos TEXT,
 opsysPreferred TEXT
);

CREATE TABLE glassthrough (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 source TEXT,
 id TEXT,
 name TEXT,
 year TEXT,
 segmenta TEXT,
 segmentb TEXT
);

CREATE TABLE gmplsFailure (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 id TEXT,
 name TEXT
);

CREATE TABLE guardband (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 startchan TEXT,
 width TEXT
);

CREATE TABLE iOMSPRcvOA (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 OAtype TEXT,
 pldm TEXT,
 pldmInDcmNetwork TEXT,
 pldmInNoDcmNetwork TEXT,
 oppcout TEXT,
 oppcout88 TEXT,
 allowedOtherOAList TEXT,
 supportedOnWR TEXT
);

CREATE TABLE iOMSPXmtOA (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 OAtype TEXT,
 pldm TEXT,
 pldmInDcmNetwork TEXT,
 pldmInNoDcmNetwork TEXT,
 oppcin TEXT,
 oppcout TEXT,
 oppcout88 TEXT,
 allowedOtherOAList TEXT,
 supportedOnWR TEXT
);

CREATE TABLE ilaShelfTypeConfig (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 ilaMainShelfType TEXT,
 ilaExtensionShelfTypeGeneralUse TEXT
);

CREATE TABLE interface (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 type TEXT
);

CREATE TABLE itl (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 source TEXT,
 id TEXT,
 packIDRef TEXT,
 year TEXT,
 type TEXT
);

CREATE TABLE line (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 source TEXT,
 id TEXT,
 currentProject TEXT,
 isDeployed TEXT,
 year TEXT,
 capacity TEXT,
 span TEXT,
 wdmlink TEXT,
 linenumber TEXT,
 linetype TEXT,
 rcvDirectionLBO TEXT,
 xmtDirectionLBO TEXT,
 oscsfp TEXT,
 oscsfpapn TEXT,
 oscsfpVOA TEXT,
 isOscSfpUserCreated TEXT,
 ssdetails TEXT,
 isUserCreated TEXT,
 isSchematicCreated TEXT,
 allowRecalculation TEXT,
 ptpio TEXT,
 monotdr TEXT,
 BandSplitter TEXT,
 isOLP TEXT,
 isOMDCLequipped TEXT,
 ServiceLaunchAtten TEXT,
 thrulineid TEXT,
 DeltaLossForCwithL TEXT
);

CREATE TABLE list (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE maxGainNotUsedPort (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE maxGainPort (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE maxGainPortL (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE minGainPort (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE minGainPortL (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE modeType (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 mode TEXT
);

CREATE TABLE ne (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 source TEXT,
 name TEXT,
 id TEXT,
 currentProject TEXT,
 isDeployed TEXT,
 year TEXT,
 netype TEXT,
 nefamilyRelease TEXT,
 opticalEquipment TEXT,
 otPlacement TEXT,
 AC_POWER_VARIANT TEXT,
 PhMNodeName TEXT,
 ShelfWidth TEXT,
 RUVerticalSpace TEXT,
 isUserDefined TEXT
);

CREATE TABLE nelist (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE nodeRestriction (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 oadmType TEXT,
 maxDegree TEXT,
 minDegree TEXT
);

CREATE TABLE oadmShelfTypeConfig (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 oadmMainShelfType TEXT,
 oadmExtensionShelfTypeGeneralUse TEXT,
 oadmExtensionShelfTypeClientLine TEXT
);

CREATE TABLE omdConfig (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 omdLineConfig TEXT
);

CREATE TABLE omdline (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 id TEXT,
 wdmline TEXT
);

CREATE TABLE oscVoaSetPort (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE oscVoaSetPortL (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE otpneMEShelfTypeConfig (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 otpneMEMainShelfType TEXT,
 otpneMEExtensionShelfTypeGeneralUse TEXT,
 otpneMEExtensionShelfTypeClientLine TEXT
);

CREATE TABLE otpneShelfTypeConfig (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 otpneMainShelfType TEXT
);

CREATE TABLE outputNotUsedPowerPort (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE outputPowerPort (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE outputPowerPortL (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE param (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 name TEXT,
 value TEXT
);

CREATE TABLE paramList (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE perChannelOutputPowerPort (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE perChannelOutputPowerPortL (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE port (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 source TEXT,
 id TEXT,
 year TEXT,
 connectortype TEXT,
 portnumber TEXT,
 conn TEXT,
 fec TEXT,
 pluggable TEXT,
 pluggableapn TEXT,
 manualapn TEXT,
 eVOAPluggable TEXT,
 evoaconnid TEXT,
 owner TEXT,
 number TEXT,
 chan TEXT,
 dropped TEXT,
 connType TEXT,
 lbo TEXT,
 cascade TEXT,
 AddLoss TEXT,
 AddLossStDev TEXT,
 DropLoss TEXT,
 DropLossStDev TEXT,
 AddLossDev TEXT,
 DropLossDev TEXT,
 applyToPorts TEXT,
 conn1f TEXT,
 isrxportfor1f TEXT
);

CREATE TABLE portPowerInPort (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE portPowerInPortL (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE portclient (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 Id TEXT,
 Ststimeslot TEXT,
 Release TEXT
);

CREATE TABLE portinterface (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 type TEXT,
 Ststimeslot TEXT
);

CREATE TABLE preampBandDetail (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 bandType TEXT,
 preamppower TEXT,
 preampinpower TEXT,
 preampdelta TEXT,
 preampgain TEXT,
 preampNoiseFigure TEXT,
 preampOSNR TEXT,
 preampinlinrip TEXT,
 preamplinrip TEXT,
 preampinrandrip TEXT,
 preamprandrip TEXT,
 preampgainsource TEXT,
 ramanEffectivePumpPowerOPSYS TEXT,
 preampgainOPSYS TEXT
);

CREATE TABLE primclientinterface (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 portnumber TEXT,
 client TEXT,
 pluginterface TEXT,
 Lineport TEXT,
 protection TEXT,
 maxMapping TEXT
);

CREATE TABLE project (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 source TEXT,
 id TEXT,
 name TEXT,
 description TEXT,
 retainrouting TEXT,
 isImport TEXT,
 year TEXT
);

CREATE TABLE ramanSignalOutputPowerPort (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE ramanTotalInputPowerPort (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE rcvOADetail (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 bandType TEXT,
 rxoa TEXT,
 gainType TEXT,
 equippedOA TEXT,
 rxoa_erules TEXT,
 gainType_erules TEXT
);

CREATE TABLE restorationRoute (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 failure TEXT,
 reusedFailure TEXT
);

CREATE TABLE route (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE rxBandDetail (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 bandType TEXT,
 rxpowertarget TEXT,
 rxtiltprov TEXT,
 rxtilttarget TEXT,
 rxtilterror TEXT,
 rxpower TEXT,
 rxdelta TEXT,
 rxinpower TEXT,
 rxOSNR TEXT,
 rxintilt TEXT,
 rxouttilt TEXT,
 rxindelta TEXT,
 rxinlinrip TEXT,
 rxPMD TEXT,
 rxPDL TEXT,
 srstiltin TEXT,
 rxVOA TEXT,
 rxVoaOPSYS TEXT
);

CREATE TABLE save (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 release TEXT,
 build TEXT,
 date TEXT,
 actions TEXT,
 wseptbuild TEXT
);

CREATE TABLE saveList (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE segmentlist (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE segt (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 source TEXT,
 id TEXT,
 name TEXT,
 currentProject TEXT,
 isDeployed TEXT,
 supportedBand TEXT,
 capacity TEXT,
 wtocm TEXT,
 wtocm_l TEXT,
 symmetric TEXT,
 inLineProtection TEXT,
 supportsOSC TEXT,
 isControlPlane TEXT,
 dcm TEXT,
 year TEXT,
 asite TEXT,
 bsite TEXT,
 otdr_tx_atob TEXT,
 otdr_rx_atob TEXT,
 mon_otdr_a TEXT,
 otdr_type_atob TEXT,
 otdr_tx_btoa TEXT,
 otdr_rx_btoa TEXT,
 otdr_type_btoa TEXT,
 mon_otdr_b TEXT,
 monOCMType_Rx_aSite TEXT,
 monOCMType_Tx_aSite TEXT,
 monOCMType_Rx_bSite TEXT,
 monOCMType_Tx_bSite TEXT,
 BandSplitter TEXT,
 isDwdm1Fiber TEXT,
 omdcl_aSite TEXT,
 omdcl_bSite TEXT,
 core TEXT,
 orient TEXT,
 description TEXT
);

CREATE TABLE segtinfo (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 orient TEXT,
 dist TEXT,
 lossmargin TEXT,
 loss TEXT,
 connlossA TEXT,
 connlossB TEXT,
 maxchannel TEXT,
 maxchannel88 TEXT,
 pmd TEXT,
 disp TEXT,
 fibertype TEXT
);

CREATE TABLE segtroute (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE sfd (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 source TEXT,
 id TEXT,
 year TEXT,
 type TEXT,
 packIDRef TEXT,
 shelf TEXT
);

CREATE TABLE shelf (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 source TEXT,
 id TEXT,
 currentProject TEXT,
 isDeployed TEXT,
 year TEXT,
 type TEXT,
 depth TEXT,
 installationKit TEXT,
 number TEXT,
 shelfCover TEXT,
 DCMcontainerID TEXT,
 apn TEXT,
 PfdcaAmperage TEXT,
 breakerSize TEXT,
 breakerUserDefined TEXT,
 isFanDefault TEXT,
 isToBeRemoved TEXT,
 shelf TEXT,
 release TEXT,
 description TEXT
);

CREATE TABLE shelfType (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 type TEXT,
 onlyForUpstreamPack TEXT,
 Release TEXT,
 shelf TEXT
);

CREATE TABLE shelfTypeConfig (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 mainShelfType TEXT,
 extensionShelfTypeGeneralUse TEXT,
 extensionShelfTypeClientLine TEXT
);

CREATE TABLE shelfset (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 id TEXT,
 source TEXT,
 name TEXT,
 currentProject TEXT,
 isDeployed TEXT,
 year TEXT,
 type TEXT,
 roadmtype TEXT,
 forceManualPowerMode TEXT,
 localAddDrop TEXT,
 MaxPSCSectionsPerOpticalLine TEXT,
 SharePSCamongWdmLines TEXT,
 ne TEXT,
 maxroadmdegree TEXT,
 maxAddDropDegree TEXT,
 isUserCreated TEXT,
 mlfsb_forceEndTerminalNode TEXT,
 allowHeterogeneousNode TEXT,
 mshFixedCabling TEXT,
 WTOCMonILA TEXT,
 dge TEXT,
 dgeFilterType TEXT
);

CREATE TABLE signalOutputNotUsedPowerPort (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE site (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 source TEXT,
 id TEXT,
 name TEXT,
 currentProject TEXT,
 isDeployed TEXT,
 year TEXT,
 allowWDM TEXT,
 etr TEXT,
 clustered TEXT,
 AnssiQSconfigured TEXT,
 EncryptedECneeded TEXT,
 allowPacket TEXT,
 maxOADMDegree TEXT,
 oadmchoice TEXT,
 lineIsolation TEXT,
 lineIsolationOnWTOCM TEXT,
 pduType TEXT,
 pduNumberOfSiteJumperKits TEXT,
 pduIncludeSliderKit TEXT,
 pduIncludeBreakerToggle TEXT,
 PSS16II_AC_POWER TEXT,
 PSS16II_ILAFanCapacity TEXT,
 includeRacks TEXT,
 shelfWidthPSS TEXT,
 shelfWidthPSIM TEXT,
 shelfWidthPSIL TEXT,
 shelfWidthPSI2T TEXT,
 RUVerticalSpacePSS TEXT,
 RUVerticalSpacePSIM TEXT,
 RUVerticalSpacePSIL TEXT,
 RUVerticalSpacePSI2T TEXT,
 passthruoptions TEXT,
 opsyspassthruoptions TEXT,
 RequireROADM TEXT,
 core TEXT,
 ForceSFD44 TEXT,
 WTOCMonILA TEXT,
 Segregation_OT TEXT,
 useLowLatencyDCMsInNonModularOAs TEXT,
 pss8cntrlprot TEXT,
 pss16cntrlprot TEXT,
 pss16IIcntrlprot TEXT,
 pss32cntrlprot TEXT,
 psi8Lcntrlprot TEXT,
 psi4Lcntrlprot TEXT,
 psimcntrlprot TEXT,
 OTDR_in_separate_shelf TEXT,
 OT_in_separate_shelf_for_CDCF TEXT,
 OT_in_separate_shelf TEXT,
 MCS_in_separate_shelf TEXT,
 lat TEXT,
 long TEXT,
 lockLatLong TEXT,
 xcoord TEXT,
 ycoord TEXT,
 FloorAndRoom TEXT,
 maxAislesPerRoom TEXT,
 maxBaysPerAisle TEXT,
 NERegenMode TEXT,
 description TEXT
);

CREATE TABLE skipChannel (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 chan TEXT
);

CREATE TABLE slot (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 slot TEXT
);

CREATE TABLE slotExclusion (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 slot TEXT
);

CREATE TABLE span (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 ashelfset TEXT,
 source TEXT,
 bshelfset TEXT,
 id TEXT,
 name TEXT,
 hideUploadUserSelectedMismatches TEXT,
 currentProject TEXT,
 isDeployed TEXT,
 year TEXT,
 orient TEXT,
 GMPLSAdminCost TEXT
);

CREATE TABLE src (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 id TEXT,
 prot TEXT,
 disjointProt TEXT,
 primshelfset TEXT,
 otPlacement TEXT,
 primsite TEXT,
 primnetype TEXT,
 primOT TEXT,
 routingOT TEXT,
 primOTLinePort TEXT,
 primLinePortPlug TEXT,
 primlayer TEXT,
 backlayer TEXT,
 sharePrimOT TEXT,
 primeAddDropConfig TEXT,
 primeMultiDirAllowed TEXT,
 backAddDropConfig TEXT,
 backMultiDirAllowed TEXT,
 year TEXT,
 encryptOT TEXT,
 encryptOTClientPort TEXT,
 ActualAddDropConfig TEXT,
 type TEXT,
 pluggableOTType TEXT,
 DeliveredOSNR TEXT,
 shelfset TEXT,
 ssdetails TEXT,
 RequiredOSNR TEXT,
 DeliveredPwr TEXT,
 MinDeliveredPwr TEXT,
 MinDeliveredOSNR TEXT,
 ResDisp1528 TEXT,
 ResDisp1546 TEXT,
 ResDisp1565 TEXT,
 NLP TEXT,
 PMD TEXT,
 PDL TEXT,
 XPM TEXT,
 qFactor TEXT,
 pre_fec_ber TEXT,
 weighted_filter_count TEXT,
 DeliveredOSNR_feasibility TEXT,
 RequiredOSNR_feasibility TEXT,
 NLP_feasibility TEXT,
 PMDPenalty_feasibility TEXT,
 PMD_feasibility TEXT,
 PDL_feasibility TEXT,
 PassThruPenalty_feasibility TEXT,
 ChannelMargin_feasibility TEXT,
 isDropLBOApplicable TEXT,
 isDropLBOUserDefined TEXT,
 isAddLBOApplicable TEXT,
 isAddLBOUserDefined TEXT,
 otNE TEXT,
 addLBO TEXT,
 backshelfset TEXT,
 backsite TEXT,
 backnetype TEXT,
 backOT TEXT,
 backOTLinePort TEXT,
 shareBackOT TEXT,
 AddDropConfig TEXT,
 AARType TEXT,
 ADBType TEXT,
 aseNoiseClass TEXT,
 RegenReason TEXT
);

CREATE TABLE srglist (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE system (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 autocommissionable TEXT,
 id TEXT,
 name TEXT,
 neRelease TEXT,
 type TEXT,
 allowPowerGainReCalculation TEXT,
 year TEXT
);

CREATE TABLE targetGainPort (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE targetTiltNotUsedPort (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE totalInputNotUsedPowerPort (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE totalInputPowerPort (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE totalInputPowerPortL (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE totalNotUsedPowerOutputPort (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE totalPowerOutputPort (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE totalPowerOutputPortL (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE transparentlink (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 id TEXT,
 orient TEXT,
 uni TEXT,
 valid TEXT,
 currentProject TEXT,
 isDeployed TEXT,
 year TEXT,
 mxnAdjustment TEXT,
 channel TEXT,
 fec TEXT,
 demandid TEXT,
 source TEXT,
 isOMSPTlink TEXT,
 createPackForOMSPLink TEXT,
 isViewDuplicate TEXT,
 TlinkType TEXT,
 FailureReason TEXT,
 gmplsFailure TEXT
);

CREATE TABLE txBandDetail (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 bandType TEXT,
 txpower TEXT,
 txOutVOA TEXT,
 txOutVoaOPSYS TEXT,
 txpowertarget TEXT,
 txlinepower TEXT,
 txdelta TEXT,
 txinpower TEXT,
 txOSNR TEXT,
 txlinepower_upload TEXT
);

CREATE TABLE voaSetPort (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE voaSetPortL (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT
);

CREATE TABLE wdmdemand (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 source TEXT,
 id TEXT,
 version TEXT,
 name TEXT,
 category TEXT,
 isWorkingPath TEXT,
 routeOver TEXT,
 deployedname TEXT,
 routedByUser TEXT,
 routeConvertedToUser TEXT,
 currentProject TEXT,
 isDeployed TEXT,
 year TEXT,
 status TEXT,
 GuaranteedRestorationFailed TEXT,
 linesignal TEXT,
 type TEXT,
 pktdemand TEXT,
 pktlink TEXT,
 restoration TEXT,
 routedisjointness TEXT,
 assignedChannels_primary TEXT,
 calculate_BOL TEXT,
 isControlPlane TEXT,
 isMultiregion TEXT,
 isRegenAllowed TEXT,
 independentTrail TEXT,
 d5x500compatible TEXT,
 AllowVerificationUsingMargin TEXT,
 wtKeyedStatus TEXT,
 trailVerificationSetting TEXT,
 channel TEXT,
 phaseEncoding TEXT,
 primaryTrail TEXT,
 disjointTrail TEXT,
 secondaryTrail TEXT,
 assignedChannels_protected TEXT,
 isMRNActivated TEXT
);

CREATE TABLE wdmlink (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 source TEXT,
 id TEXT,
 name TEXT,
 currentProject TEXT,
 isDeployed TEXT,
 year TEXT,
 status TEXT,
 ashelfset TEXT,
 capacity TEXT,
 bshelfset TEXT,
 maxUsableChannelCount TEXT,
 maxUsableChannelCount_L TEXT,
 abPowerOffsets TEXT,
 technology TEXT,
 rxchannelfor1f TEXT,
 isUserCreated TEXT,
 isForceRecalc TEXT,
 isUserTracking TEXT,
 bandingFlexStartChannel TEXT,
 bandingFlexChannel TEXT,
 bandingFlexStartChannel_L TEXT,
 bandingFlexChannel_L TEXT,
 egressAdjustmentForABDirection TEXT,
 egressAdjustmentForBADirection TEXT,
 supportedBand TEXT,
 numNodewith1WSS TEXT,
 numNodewith2WSS TEXT,
 aendCDSpanInput1830LX TEXT,
 bendCDSpanInput1830LX TEXT,
 linkCountC TEXT,
 linkCountL TEXT,
 isASELLoading TEXT,
 powerOffsetSetting TEXT,
 orient TEXT,
 baPowerOffsets TEXT
);

CREATE TABLE wdmpack (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 primpackref TEXT,
 packref TEXT,
 portref1 TEXT,
 backpackref TEXT,
 portref2 TEXT
);

CREATE TABLE xmtOADetail (
 parentId TEXT,
 parentTag TEXT,
 parentAttrs TEXT,
 grandparentId TEXT,
 grandparentTag TEXT,
 grandparentAttrs TEXT,
 bandType TEXT,
 txoa TEXT,
 gainType TEXT,
 equippedOA TEXT,
 txoa_erules TEXT,
 gainType_erules TEXT
);

COMMIT;
