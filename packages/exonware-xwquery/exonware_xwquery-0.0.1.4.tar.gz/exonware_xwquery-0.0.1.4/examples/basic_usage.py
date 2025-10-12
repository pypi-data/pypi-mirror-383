#!/usr/bin/env python3
"""
Basic XWQuery usage examples.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 11, 2025
"""

from exonware.xwquery import XWQuery

# Example data
users = [
    {'id': 1, 'name': 'Alice', 'age': 30, 'city': 'NYC', 'active': True},
    {'id': 2, 'name': 'Bob', 'age': 25, 'city': 'LA', 'active': True},
    {'id': 3, 'name': 'Charlie', 'age': 35, 'city': 'NYC', 'active': False},
    {'id': 4, 'name': 'Diana', 'age': 28, 'city': 'Chicago', 'active': True},
]


def example_1_basic_select():
    """Example 1: Basic SELECT query."""
    print("\n" + "="*60)
    print("Example 1: Basic SELECT")
    print("="*60)
    
    query = "SELECT * FROM users WHERE age > 25"
    print(f"Query: {query}")
    print(f"Validation: {XWQuery.validate(query)}")


def example_2_projection():
    """Example 2: SELECT with projection."""
    print("\n" + "="*60)
    print("Example 2: Projection")
    print("="*60)
    
    query = "SELECT name, age FROM users WHERE city = 'NYC'"
    print(f"Query: {query}")
    print(f"Validation: {XWQuery.validate(query)}")


def example_3_aggregation():
    """Example 3: Aggregation query."""
    print("\n" + "="*60)
    print("Example 3: Aggregation")
    print("="*60)
    
    query = """
    SELECT 
        city, 
        COUNT(*) as user_count,
        AVG(age) as avg_age
    FROM users
    GROUP BY city
    """
    print(f"Query: {query}")
    print(f"Validation: {XWQuery.validate(query)}")


def example_4_format_conversion():
    """Example 4: Format conversion."""
    print("\n" + "="*60)
    print("Example 4: Format Conversion")
    print("="*60)
    
    sql_query = "SELECT name, email FROM users WHERE age > 25"
    print(f"Original SQL: {sql_query}")
    
    # Convert to GraphQL
    print("\nConverting to other formats...")
    print(f"Supported formats: {', '.join(XWQuery.get_supported_formats()[:10])}")


def example_5_supported_operations():
    """Example 5: Show supported operations."""
    print("\n" + "="*60)
    print("Example 5: Supported Operations")
    print("="*60)
    
    operations = XWQuery.get_supported_operations()
    print(f"Total operations: {len(operations)}")
    print(f"\nCore operations:")
    print(f"  - CRUD: SELECT, INSERT, UPDATE, DELETE")
    print(f"  - Filtering: WHERE, FILTER, BETWEEN, LIKE, IN")
    print(f"  - Aggregation: SUM, COUNT, AVG, MIN, MAX, GROUP BY")
    print(f"  - Graph: MATCH, PATH, OUT, IN_TRAVERSE")
    print(f"  - Advanced: JOIN, UNION, WITH, PIPE")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print(" XWQuery - Basic Usage Examples")
    print("="*60)
    
    example_1_basic_select()
    example_2_projection()
    example_3_aggregation()
    example_4_format_conversion()
    example_5_supported_operations()
    
    print("\n" + "="*60)
    print(" Examples Complete!")
    print("="*60)
    print("\nNote: These examples show query validation and structure.")
    print("For actual execution, queries need to be run on XWNode structures.")
    print("See advanced examples for execution demonstrations.")


if __name__ == "__main__":
    main()

