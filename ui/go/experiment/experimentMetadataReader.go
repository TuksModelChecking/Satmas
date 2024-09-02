package experiment

type ExperimentMetadataReader interface {
	InitialiseReader() error
	CloseReader() error
	ReadAllExperimentMetadata() ([]*Metadata, error)
}
