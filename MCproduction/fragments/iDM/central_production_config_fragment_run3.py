import FWCore.ParameterSet.Config as cms
from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *
from Configuration.Generator.PSweightsPythia.PythiaPSweightsSettings_cfi import *

# link to card:
externalLHEProducer = cms.EDProducer("ExternalLHEProducer",
    args = cms.vstring('@GRIDPACK'),
    nEvents = cms.untracked.uint32(100),
    numberOfParameters = cms.uint32(1),
    outputFile = cms.string('cmsgrid_final.lhe'),
    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')
    )



generator = cms.EDFilter("Pythia8ConcurrentHadronizerFilter",
                         eventsToPrint = cms.untracked.uint32(5),
                         UseExternalGenerators = cms.untracked.bool(True),
                         maxEventsToPrint = cms.untracked.int32(1),
                         pythiaPylistVerbosity = cms.untracked.int32(1),
                         filterEfficiency = cms.untracked.double(1.0),
                         pythiaHepMCVerbosity = cms.untracked.bool(False),
                         comEnergy = cms.double(13600.),
                         PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP5SettingsBlock,
        pythia8PSweightsSettingsBlock,
        processParameters = cms.vstring(
    'Main:timesAllowErrors = 10000',
    'ParticleDecays:limitTau0 = on',
    'ParticleDecays:tau0Max = 10',
    'Check:epTolErr = 0.01',
    'SLHA:minMassSM = 10.',
    '35:onMode = off',
    '23:onMode = off',
    '24:onMode = off',
    ),
        parameterSets = cms.vstring('pythia8CommonSettings',
                                    'pythia8CP5Settings',
                                    'pythia8PSweightsSettings',
                                    'processParameters'
                                    )
        )
)

ProductionFilterSequence = cms.Sequence(generator)