import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from ..exceptions import AbromicsAPIError


@dataclass
class Sample:
    id: int
    project_id: int
    metadata: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Sample':
        return cls(
            id=data['id'],
            project_id=data['project'],
            metadata=data.get('metadata', {}),
            created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')) if data.get('updated_at') else None
        )


class SampleManager:
    def __init__(self, client):
        self.client = client
    
    def create(
        self,
        project_id: int,
        metadata: Dict[str, Any]
    ) -> Sample:
        # Get the project to find its template
        project_response = self.client.get(f'/api/project/{project_id}/')
        project_data = project_response.json()
        template_id = project_data['template']['id'] if isinstance(project_data['template'], dict) else project_data['template']
        
        
        # Get metadata templates for this template
        metadata_templates_response = self.client.get(f'/api/metadata_template/?template={template_id}')
        metadata_templates = metadata_templates_response.json()
        
        
        # Build field mapping from actual metadata templates
        field_mapping = {}
        for template in metadata_templates:
            field_name = template['field_name']
            template_id = template['id']
            field_number = template['field_number']
            
            # Handle special cases for R1/R2 filenames
            if field_name == 'original_name':
                if field_number == 3:  # R1 fastq filename
                    field_mapping['r1_fastq_filename'] = template_id
                elif field_number == 4:  # R2 fastq filename
                    field_mapping['r2_fastq_filename'] = template_id
                else:
                    field_mapping[field_name] = template_id
            else:
                field_mapping[field_name] = template_id
            
        
        
        # Build the data array in the expected format
        data_array = []
        for field_name, value in metadata.items():
            if field_name in field_mapping and value is not None:
                data_array.append({
                    "metadata_template": field_mapping[field_name],
                    "value": str(value)
                })
        
        data = {
            'project': str(project_id),  # Convert to string
            'data': [data_array]  # Array of arrays - each sample is a list of metadata items
        }
        
        try:
            # Intentionally left without debug prints in production
            # Use the raw session to avoid automatic error handling
            response = self.client.session.post(
                f"{self.client.base_url}/api/upload_data/",
                json=data,
                timeout=self.client.timeout
            )
            
            # Check if response is successful
            if response.status_code not in [200, 201]:
                raise AbromicsAPIError(f"API returned {response.status_code}: {response.text}")
            
            result = response.json()
            
            # Handle validation errors (422 status)
            if 'error' in result:
                raise AbromicsAPIError(f"Sample creation failed: {result['error']}")
            
            if isinstance(result, list) and len(result) > 0:
                sample_data = result[0]
                if 'error' in sample_data and sample_data['error']:
                    raise AbromicsAPIError(f"Sample creation failed: {sample_data['error']}")
                
                # The upload_data API returns experiment data, not sample data
                # Create a mock sample object with the experiment ID and raw input file IDs
                experiment_data = sample_data['data']
                mock_sample_data = {
                    'id': experiment_data['experiment_id'],
                    'project': project_id,
                    'metadata': metadata,
                    'created_at': None,
                    'updated_at': None,
                    'raw_input_file_ids': experiment_data.get('raw_input_files', [])
                }
                
                return Sample.from_dict(mock_sample_data)
            else:
                raise AbromicsAPIError("Unexpected response format from sample creation")
        except requests.exceptions.HTTPError as e:
            # This will catch the 400 error before it gets raised
            raise AbromicsAPIError(f"API returned {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise e
    
    def get(self, sample_id: int) -> Sample:
        response = self.client.get(f'/api/sample/{sample_id}/')
        return Sample.from_dict(response.json())
    
    def list(
        self,
        project_id: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Sample]:
        params = {}
        if project_id:
            params['project'] = project_id
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        
        response = self.client.get('/api/sample/', params=params)
        data = response.json()
        
        if 'results' in data:
            samples = data['results']
        else:
            samples = data if isinstance(data, list) else [data]
        
        return [Sample.from_dict(sample) for sample in samples]
    
    def update(
        self,
        sample_id: int,
        metadata: Dict[str, Any]
    ) -> Sample:
        data = {
            'data': [metadata]
        }
        
        response = self.client.patch(f'/api/upload_data/{sample_id}/', data=data)
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            sample_data = result[0]
            if 'error' in sample_data and sample_data['error']:
                raise AbromicsAPIError(f"Sample update failed: {sample_data['error']}")
            
            return Sample.from_dict(sample_data['data'])
        else:
            raise AbromicsAPIError("Unexpected response format from sample update")
    
    def delete(self, sample_id: int) -> bool:
        self.client.delete(f'/api/sample/{sample_id}/')
        return True
