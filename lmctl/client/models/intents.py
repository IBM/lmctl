from typing import Dict
from abc import ABC, abstractmethod

class Intent(ABC):

    @abstractmethod
    def to_dict(self) -> Dict:
        pass

class ExistingAssemblyIntent(Intent):
    
    def __init__(self, assembly_id: str = None, assembly_name: str = None):
        self.assembly_id = assembly_id
        self.assembly_name = assembly_name

    def set_assembly_id(self, assembly_id: str):
        self.assembly_id = assembly_id
        return self

    def set_assembly_name(self, assembly_name: str):
        self.assembly_name = assembly_name
        return self

    def to_dict(self) -> Dict:
        obj = {}
        if self.assembly_id is not None:
            obj['assemblyId'] = self.assembly_id
        if self.assembly_name is not None:
            obj['assemblyName'] = self.assembly_name 
        return obj

class CreateAssemblyIntent(Intent):
        
    def __init__(self, assembly_name: str = None, descriptor_name: str = None, 
                        intended_state: str = None, properties: Dict = None):
        self.assembly_name = assembly_name
        self.descriptor_name = descriptor_name
        self.intended_state = intended_state
        self.properties = properties or {}
    
    def set_assembly_name(self, assembly_name: str):
        self.assembly_name = assembly_name
        return self

    def set_descriptor_name(self, descriptor_name: str):
        self.descriptor_name = descriptor_name
        return self

    def set_intended_state(self, intended_state: str):
        self.intended_state = intended_state
        return self
    
    def set_properties(self, properties: Dict):
        self.properties = properties
        return self

    def set_property(self, name: str, value: str):
        if self.properties is None:
            self.properties = {}
        self.properties[name] = value
        return self

    def to_dict(self) -> Dict:
        obj = {}
        if self.assembly_name is not None:
            obj['assemblyName'] = self.assembly_name
        if self.descriptor_name is not None:
            obj['descriptorName'] = self.descriptor_name
        if self.properties is not None:
            obj['properties'] = self.properties
        if self.intended_state is not None:
            obj['intendedState'] = self.intended_state
        return obj

class ChangeAssemblyStateIntent(ExistingAssemblyIntent):

    def __init__(self, assembly_id: str = None, assembly_name: str = None, intended_state: str = None):
        super().__init__(assembly_id=assembly_id, assembly_name=assembly_name)
        self.intended_state = intended_state
    
    def set_intended_state(self, intended_state: str):
        self.intended_state = intended_state
        return self
    
    def to_dict(self) -> Dict:
        obj = super().to_dict()
        if self.intended_state is not None:
            obj['intendedState'] = self.intended_state
        return obj

class DeleteAssemblyIntent(ExistingAssemblyIntent):

    def __eq__(self, other):
        return (isinstance(other, DeleteAssemblyIntent) and self.assembly_name==other.assembly_name
            and self.assembly_id==other.assembly_id)

class HealAssemblyIntent(ExistingAssemblyIntent):

    def __init__(self, assembly_id: str = None, assembly_name: str = None, 
                        broken_component_id: str = None, broken_component_name: str = None, 
                        broken_component_metric_key: str = None):
        super().__init__(assembly_id=assembly_id, assembly_name=assembly_name)
        self.broken_component_id = broken_component_id
        self.broken_component_name = broken_component_name
        self.broken_component_metric_key = broken_component_metric_key
    
    def set_broken_component_id(self, broken_component_id: str):
        self.broken_component_id = broken_component_id
        return self

    def set_broken_component_name(self, broken_component_name: str):
        self.broken_component_name = broken_component_name
        return self
    
    def set_broken_component_metric_key(self, broken_component_metric_key: str):
        self.broken_component_metric_key = broken_component_metric_key
        return self
    
    def to_dict(self) -> Dict:
        obj = super().to_dict()
        if self.broken_component_id is not None:
            obj['brokenComponentId'] = self.broken_component_id
        if self.broken_component_name is not None:
            obj['brokenComponentName'] = self.broken_component_name
        if self.broken_component_metric_key is not None:
            obj['brokenComponentMetricKey'] = self.broken_component_metric_key
        return obj

class ScaleAssemblyIntent(ExistingAssemblyIntent):

    def __init__(self, assembly_id: str = None, assembly_name: str = None, 
                        cluster_name: str = None):
        super().__init__(assembly_id=assembly_id, assembly_name=assembly_name)
        self.cluster_name = cluster_name
    
    def set_cluster_name(self, cluster_name: str):
        self.cluster_name = cluster_name
        return self

    def to_dict(self) -> Dict:
        obj = super().to_dict()
        if self.cluster_name is not None:
            obj['clusterName'] = self.cluster_name
        return obj

class UpgradeAssemblyIntent(ExistingAssemblyIntent):
  
    def __init__(self, assembly_id: str = None, assembly_name: str = None, descriptor_name: str = None, 
                        intended_state: str = None, properties: Dict = None):
        super().__init__(assembly_id=assembly_id, assembly_name=assembly_name)
        self.descriptor_name = descriptor_name
        self.intended_state = intended_state
        self.properties = properties or {}
    
    def set_descriptor_name(self, descriptor_name: str):
        self.descriptor_name = descriptor_name
        return self

    def set_intended_state(self, intended_state: str):
        self.intended_state = intended_state
        return self
    
    def set_properties(self, properties: Dict):
        self.properties = properties
        return self

    def set_property(self, name: str, value: str):
        if self.properties is None:
            self.properties = {}
        self.properties[name] = value
        return self

    def to_dict(self) -> Dict:
        obj = super().to_dict()
        if self.descriptor_name is not None:
            obj['descriptorName'] = self.descriptor_name
        if self.properties is not None:
            obj['properties'] = self.properties
        if self.intended_state is not None:
            obj['intendedState'] = self.intended_state
        return obj

class CreateOrUpgradeAssemblyIntent(Intent):
        
    def __init__(self, assembly_name: str = None, descriptor_name: str = None, 
                        intended_state: str = None, properties: Dict = None,
                        tags: Dict = None):
        self.assembly_name = assembly_name
        self.descriptor_name = descriptor_name
        self.intended_state = intended_state
        self.properties = properties or {}
        self.tags = tags or {}
    
    def set_assembly_name(self, assembly_name: str):
        self.assembly_name = assembly_name
        return self

    def set_descriptor_name(self, descriptor_name: str):
        self.descriptor_name = descriptor_name
        return self

    def set_intended_state(self, intended_state: str):
        self.intended_state = intended_state
        return self
    
    def set_properties(self, properties: Dict):
        self.properties = properties
        return self

    def set_property(self, name: str, value: str):
        if self.properties is None:
            self.properties = {}
        self.properties[name] = value
        return self

    def set_tags(self, tags: Dict):
        self.tags = tags
        return self

    def set_tag(self, name: str, value: str):
        if self.tags is None:
            self.tags = {}
        self.tags[name] = value
        return self

    def to_dict(self) -> Dict:
        obj = {}
        if self.assembly_name is not None:
            obj['assemblyName'] = self.assembly_name
        if self.descriptor_name is not None:
            obj['descriptorName'] = self.descriptor_name
        if self.properties is not None:
            obj['properties'] = self.properties
        if self.tags is not None:
            obj['tags'] = self.tags
        if self.intended_state is not None:
            obj['intendedState'] = self.intended_state
        return obj

    def __str__(self):
        return (
            f"assembly_name={self.assembly_name}, "
            f"descriptor_name={self.descriptor_name}, "
            f"intended_state={self.intended_state}, "
            f"properties={self.properties}, "
            f"tags={self.tags}"
        )

    def __eq__(self, other):
        return (isinstance(other, CreateOrUpgradeAssemblyIntent) and self.assembly_name==other.assembly_name
            and self.descriptor_name==other.descriptor_name and self.intended_state==other.intended_state
            and self.properties==other.properties)
            

class AdoptAssemblyIntent(Intent):

    def __init__(self, assembly_name: str = None, descriptor_name: str = None,
            properties: Dict = None, clusters: Dict = None):
        self.assembly_name = assembly_name
        self.descriptor_name = descriptor_name
        self.properties = properties or {}
        self.clusters = clusters or {}

    def set_assembly_name(self, assembly_name: str):
        self.assembly_name = assembly_name
        return self

    def set_descriptor_name(self, descriptor_name: str):
        self.descriptor_name = descriptor_name
        return self
    
    def set_properties(self, properties: Dict):
        self.properties = properties
        return self

    def set_property(self, name: str, value: str):
        if self.properties is None:
            self.properties = {}
        self.properties[name] = value
        return self

    def set_clusters(self, clusters: Dict):
        self.clusters = clusters
        return self
    
    def set_cluster(self, name: str, value: int):
        if self.clusters is None:
            self.clusters = {}
        self.clusters[name] = value
        return self

    def to_dict(self) -> Dict:
        obj = {}
        if self.assembly_name is not None:
            obj['assemblyName'] = self.assembly_name
        if self.descriptor_name is not None:
            obj['descriptorName'] = self.descriptor_name
        if self.properties is not None:
            obj['properties'] = self.properties
        if self.clusters is not None:
            obj['clusters'] = self.clusters
        return obj