"""
Example script demonstrating the OpenAPI to Postman converter.
This script can be run standalone to test the conversion functionality.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from devops_toolset.project_types.postman.openapi_to_postman import OpenAPIToPostmanConverter


def example_petstore_api():
    """
    Example: Convert the Swagger Petstore API to Postman collection.
    """
    print("Example 1: Converting Swagger Petstore API")
    print("-" * 60)
    
    converter = OpenAPIToPostmanConverter(
        openapi_source="https://petstore3.swagger.io/api/v3/openapi.json",
        output_folder="./examples/petstore_output",
        environments=["development", "staging", "production"]
    )
    
    try:
        result = converter.convert()
        
        print("\n✓ Conversion successful!")
        print(f"  API: {result['api_title']} v{result['api_version']}")
        print(f"  Collection: {result['collection']}")
        print(f"  Environments: {len(result['environments'])} files")
        
        for env_file in result['environments']:
            print(f"    - {Path(env_file).name}")
            
        return result
        
    except Exception as e:
        print(f"\n✗ Conversion failed: {str(e)}")
        return None


def example_local_yaml():
    """
    Example: Convert a local YAML OpenAPI specification.
    Note: This example requires a local OpenAPI file to exist.
    """
    print("\n\nExample 2: Converting local YAML file")
    print("-" * 60)
    
    # Check if example file exists
    openapi_file = "./examples/api-spec.yaml"
    
    if not Path(openapi_file).exists():
        print(f"⚠ Skipping: Example file not found: {openapi_file}")
        print("  Create an OpenAPI YAML file at this location to test local file conversion.")
        return None
    
    converter = OpenAPIToPostmanConverter(
        openapi_source=openapi_file,
        output_folder="./examples/local_output",
        environments=["staging", "production"]
    )
    
    try:
        result = converter.convert()
        
        print("\n✓ Conversion successful!")
        print(f"  API: {result['api_title']} v{result['api_version']}")
        print(f"  Collection: {result['collection']}")
        
        return result
        
    except Exception as e:
        print(f"\n✗ Conversion failed: {str(e)}")
        return None


def example_custom_configuration():
    """
    Example: Custom configuration with minimal environments.
    """
    print("\n\nExample 3: Custom configuration")
    print("-" * 60)
    
    converter = OpenAPIToPostmanConverter(
        openapi_source="https://petstore3.swagger.io/api/v3/openapi.json",
        output_folder="./examples/custom_output",
        environments=["local"]  # Single environment
    )
    
    try:
        result = converter.convert()
        
        print("\n✓ Conversion successful!")
        print(f"  Generated for single environment: local")
        print(f"  Collection: {result['collection']}")
        
        return result
        
    except Exception as e:
        print(f"\n✗ Conversion failed: {str(e)}")
        return None


def main():
    """
    Run all examples.
    """
    print("=" * 60)
    print("OpenAPI to Postman Converter - Examples")
    print("=" * 60)
    print()
    
    # Run examples
    example_petstore_api()
    example_local_yaml()
    example_custom_configuration()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
    print("\nCheck the ./examples/ directory for generated files.")
    print("\nTo use generated files:")
    print("  1. Import the collection JSON file into Postman")
    print("  2. Import the environment JSON files into Postman")
    print("  3. Configure authentication variables (tenantId, clientId, etc.)")
    print("  4. Send the 'Get JWT Token' request to authenticate")
    print("  5. Use the API endpoints with the obtained token")


if __name__ == "__main__":
    main()
