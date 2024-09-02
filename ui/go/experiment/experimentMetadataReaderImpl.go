package experiment

var _ ExperimentMetadataReader = &ExperimentMetadataReaderImpl{}

type ExperimentMetadataReaderImpl struct {
	experimentStore *Store
}

func NewExperimentMetadataReaderImpl(experimentStore *Store) *ExperimentMetadataReaderImpl {
	return &ExperimentMetadataReaderImpl{
		experimentStore: experimentStore,
	}
}

func (e *ExperimentMetadataReaderImpl) InitialiseReader() error {
	if err := e.experimentStore.ReadMetadataFromFile(); err != nil {
		return err
	}
	return nil
}

func (e *ExperimentMetadataReaderImpl) CloseReader() error {
	if err := e.experimentStore.WriteMetadataToFile(); err != nil {
		return err
	}
	return nil
}

func (e *ExperimentMetadataReaderImpl) ReadAllExperimentMetadata() ([]*Metadata, error) {
	return e.experimentStore.RetrieveMetadata()
}
