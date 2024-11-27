from django.shortcuts import render
from django.db import connection
import sys

from collections import defaultdict

import re


from .forms import SQLQueryForm, SQLValidationForm

import pandas as pd  # type: ignore

from pyspark.sql import SparkSession

from django.conf import settings

from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark import SparkContext, SparkConf
from pyspark.conf import SparkConf
# from pyspark.sql.types import StructType, StructField, StringType, IntegerType  # Import these classes
import json
from django.http import JsonResponse

import os
import sys  # Import sys module to access Python version



# Initialize PySpark session
spark = SparkSession.builder.appName('SourceTargetValidation').getOrCreate()

def get_spark_session():
    spark = (SparkSession
                    .builder
                    .master("local[*]")  # Use local mode with all cores
                    .appName('SourceTargetValidation')
                    .getOrCreate()
                )
    
    return spark

def sparkdataProcessing(request):
    # spark = get_spark_session()
    
    with connection.cursor() as cursor:
    
        # Execute a raw SQL query to select all data from your table
        cursor.execute("SELECT id, title, content FROM blog_management_blog")
        
        # Fetch all rows from the executed query
        rows = cursor.fetchall()

        # Optionally, fetch column names for better rendering in the template
        columns = [col[0] for col in cursor.description]

    # Create a simple DataFrame
    df = spark.createDataFrame(rows, columns)
    
    result = df.collect()
    result_list = [{"id": row["id"],
                    "title": row["title"], 
                    "content": row["content"]
                     } for row in result]
        
    # Pass the rows and column names to the template,
    return render(request, "validation_app/sparkdataProcessing.html", {"result_list": result_list})
    

def execute_sql(query):
    """Execute SQL on the Django database and return Pandas DataFrame."""
    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        data = cursor.fetchall()
    return pd.DataFrame(data, columns=columns)

def execute_pyspark_sql(query):
    """Execute SQL on PySpark and return DataFrame."""
    return spark.sql(query)

def fill_nulls(df, is_big_data=False):
    """Fill null values with defaults."""
    if is_big_data:
        for col, dtype in df.dtypes:
            if dtype == 'string':
                df = df.fillna({col: ''})
            elif dtype in ('int', 'bigint', 'double', 'float'):
                df = df.fillna({col: 0})
    else:
        for col in df.columns:
            if df[col].dtype == 'object':  # Strings
                df[col].fillna('', inplace=True)
            elif pd.api.types.is_numeric_dtype(df[col]):  # Numeric
                df[col].fillna(0, inplace=True)
    return df

def compare_dataframes(source, target):
    """Compare source and target DataFrames and return analytics."""
    # Matched records
    matched_records = pd.merge(source, target, how="inner")
    
    # Unmatched records
    unmatched_source = pd.concat([source, matched_records]).drop_duplicates(keep=False)
    unmatched_target = pd.concat([target, matched_records]).drop_duplicates(keep=False)
    
    # Analytics
    analytics = {
        "row_count": {
            "source": len(source),
            "target": len(target),
            "matched": len(matched_records),
            "unmatched_source": len(unmatched_source),
            "unmatched_target": len(unmatched_target),
        },
        "matched_records": matched_records,
        "unmatched_source": unmatched_source,
        "unmatched_target": unmatched_target,
    }
    return analytics


def sql_validation_view(request):
    analytics = None
    if request.method == "POST":
        form = SQLValidationForm(request.POST)
        if form.is_valid():
            source_sql = form.cleaned_data['source_sql']
            target_sql = form.cleaned_data['target_sql']

            # Execute queries
            source_df = execute_sql(source_sql)
            target_df = execute_sql(target_sql)

            # Fill null values
            source_df = fill_nulls(source_df)
            target_df = fill_nulls(target_df)

            # Compare dataframes and generate analytics
            analytics = compare_dataframes(source_df, target_df)
    else:
        form = SQLValidationForm()

    return render(request, 'validation_app/sql_validation.html', {'form': form, 'analytics': analytics})



# ####################################################################

def execute_sql_with_join_type(request):
    results = None
    columns = None
    error = None
    analytics = {
        "Total Rows": 0,
        "Null Counts": {},
        "Missing Records": {}  # To store missing record details
    }
    
    if request.method == 'POST':
        form = SQLQueryForm(request.POST)
        if form.is_valid():
            sql_query = form.cleaned_data['sql_query']
            join_type = form.cleaned_data['join_type']  # Get the selected join type
            try:
                # Replace join type in the query if required (optional, based on your logic)
                if join_type != "NO_CHANGE":
                    sql_query = sql_query.replace('JOIN', join_type)
                
                
                with connection.cursor() as cursor:
                    cursor.execute(sql_query)
                    columns = [col[0] for col in cursor.description]  # Extract column names
                    results = cursor.fetchall()  # Get query results
                    
                    # # Calculate analytics (total rows, null counts)
                    # if results:
                    #     total_rows = len(results)
                    #     null_counts = {
                    #         col: sum(1 for row in results if row[idx] is None)
                    #         for idx, col in enumerate(columns)
                    #     }
                    #     analytics = {
                    #                     'total_rows': total_rows,  # Use snake_case without spaces
                    #                     'null_counts': null_counts,  # Adjust this as well
                    #                 }


                    # # Analyze results for null counts and total rows
                    # analytics["Total Rows"] = len(results)
                    
                    # # Initialize Null Counts dictionary
                    # # Assuming column names are the first row of results (or defined elsewhere)
                    # column_names = [col[0] for col in cursor.description]  # Get column names
                    # analytics["Null Counts"] = {col: 0 for col in column_names}

                    # # Count null values in each column
                    # for row in results:
                    #     for idx, value in enumerate(row):
                    #         if value is None:
                    #             column_name = column_names[idx]
                    #             analytics["Null Counts"][column_name] += 1



                    analytics["Total_Rows"] = len(results)
                    
                    # Initialize Null Counts and Missing Records dictionaries
                    column_names = [col[0] for col in cursor.description]  # Get column names
                    analytics["Null_Counts"] = {col: 0 for col in column_names}
                    analytics["Missing_Records"] = {col: "" for col in column_names}

                    # Count null values and track missing records based on JOIN type
                    for row in results:
                        for idx, value in enumerate(row):
                            column_name = column_names[idx]
                            if value is None:
                                analytics["Null Counts"][column_name] += 1
                                
                                # Identify missing record from left or right table
                                if join_type == "LEFT JOIN":
                                    # Missing records in the right table will have null values for columns from the right table
                                    if column_name.startswith("c."):  # Example: column from the right table (e.g., 'c.author')
                                        analytics["Missing Records"][column_name] = "Missing in RIGHT table"
                                elif join_type == "RIGHT JOIN":
                                    # Missing records in the left table will have null values for columns from the left table
                                    if not column_name.startswith("c."):  # Example: column from the left table (e.g., 'b.title')
                                        analytics["Missing Records"][column_name] = "Missing in LEFT table"
                                elif join_type == "INNER JOIN":
                                    # In INNER JOIN, no NULLs should be there, but still track
                                    if column_name.startswith("c."):
                                        analytics["Missing Records"][column_name] = "Missing in RIGHT table"
                                    elif not column_name.startswith("c."):
                                        analytics["Missing Records"][column_name] = "Missing in LEFT table"
                                elif join_type == "FULL OUTER JOIN":
                                    # FULL OUTER JOIN: NULLs can appear in both tables
                                    if column_name.startswith("c."):
                                        analytics["Missing Records"][column_name] = "Missing in RIGHT table"
                                    elif not column_name.startswith("c."):
                                        analytics["Missing Records"][column_name] = "Missing in LEFT table"

            except Exception as e:
                error = str(e)
    else:
        form = SQLQueryForm()
    
    return render(request, 'validation_app/sql_query_form.html', {
        'form': form,
        'columns': columns,
        'results': results,
        'analytics': analytics,
        'error': error,
    })


def execute_sql_with_join_type_xx(request):
    results = None
    error = None
    columns = []
    analytics = defaultdict(dict)
    # analytics = {}

    if request.method == 'POST':
        sql_query = request.POST.get('sql_query', '').strip()  # Original SQL query
        join_type = request.POST.get('join_type', 'INNER JOIN').strip()  # Join type (e.g., INNER JOIN, LEFT JOIN)
        form = SQLQueryForm(request.POST)

        if sql_query:
            try:
                with connection.cursor() as cursor:
                    # Parse the SQL query and replace the join type
                    modified_query = replace_join_type(sql_query, join_type)

                    # Execute the modified query
                    print(f"Executing Query with {join_type}:", modified_query)  # Debugging
                    cursor.execute(modified_query)
                    columns = [col[0] for col in cursor.description]
                    results = cursor.fetchall()

                    # Analyze total record counts for the involved tables
                    tables = extract_table_names(sql_query)  # Extract table names for analysis
                    for table in tables:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        total_count = cursor.fetchone()[0]
                        analytics[table]['total_count'] = total_count

                    

            except Exception as e:
                error = str(e)
    else:
        form = SQLQueryForm()

    return render(request, 'validation_app/sql_query_form.html', {
        'form': form,
        'columns': columns,
        'results': results,
        'analytics': analytics,
        'error': error,
    })


def replace_join_type(sql_query, join_type):
    """
    Replace the join type in the SQL query with the specified join type.
    """
    # Regex to find join type in SQL query
    join_pattern = re.compile(r'\b(INNER JOIN|LEFT JOIN|RIGHT JOIN|FULL OUTER JOIN|JOIN)\b', re.IGNORECASE)
    modified_query = re.sub(join_pattern, join_type, sql_query)
    return modified_query


def extract_table_names(sql_query):
    """
    Extract table names from the SQL query for analytics.
    """
    table_names = []
    # Basic regex to find table names (after FROM or JOIN keywords)
    table_pattern = re.compile(r'\b(FROM|JOIN)\s+(\w+)', re.IGNORECASE)
    matches = table_pattern.findall(sql_query)
    for match in matches:
        table_names.append(match[1])  # Capture the table name
    return table_names

def execute_sql_query(request):
    results = None
    columns = []  # Default to an empty list
    error = None

    if request.method == 'POST':
        form = SQLQueryForm(request.POST)
        if form.is_valid():
            # query = form.cleaned_data['sql_query']
            query = 'select * from blog_management_blog'
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    if cursor.description:  # Extract column names
                        columns = [col[0] for col in cursor.description]
                    # Get column names if the query has a result set
                    if query.lower().strip().startswith("select"):
                        results = cursor.fetchall()
                        # print(columns)
                        # sys.exit()
                    else:
                        connection.commit()
            except Exception as e:
                error = str(e)
    else:
        form = SQLQueryForm()

    return render(request, 'validation_app/sql_query_form.html', {
        'form': form,
        'columns': columns,  # Pass column names to template
        'results': results,
        'error': error
    })


def validation_type_xx(request):
    columns = None  # Ensure columns is initialized
    results = None
    error = None

    if request.method == 'POST':
        form = SQLQueryForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['sql_query']
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    if query.lower().strip().startswith("select"):
                        columns = [col[0] for col in cursor.description]
                        results = cursor.fetchall()
                    else:
                        connection.commit()
            except Exception as e:
                error = str(e)
    else:
        form = SQLQueryForm()

    return render(request, 'validation_app/sql_query_form.html', {
        'form': form,
        'columns': columns,
        'results': results,
        'error': error
    })



def validation_type_ok(request):
    results = None
    error = None
    total_count = None
    total_nulls = None
    mismatches = None
    matches = None
    columns = []

    if request.method == 'POST':
        form = SQLQueryForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['sql_query']
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)

                    # Extract columns from the query result
                    columns = [col[0] for col in cursor.description]

                    if query.lower().strip().startswith("select"):
                        # Fetch the actual data
                        results = cursor.fetchall()

                        # Calculate Total Count
                        cursor.execute("SELECT COUNT(*) FROM (" + query + ") AS total_count")
                        total_count = cursor.fetchone()[0]

                        # Calculate Total Nulls for each column
                        total_nulls = {}
                        for col in columns:
                            cursor.execute(f"SELECT COUNT(*) FROM ({query}) AS t WHERE {col} IS NULL")
                            total_nulls[col] = cursor.fetchone()[0]

                        # If the query includes a JOIN, find mismatches and matches
                        if "JOIN" in query.upper():
                            # Find total mismatched records
                            # Assuming the query joins two tables using 'id'
                            cursor.execute(f"SELECT COUNT(*) FROM ({query}) AS t WHERE t.id IS NULL")
                            mismatches = cursor.fetchone()[0]

                            # Find total matched records
                            cursor.execute(f"SELECT COUNT(*) FROM ({query}) AS t WHERE t.id IS NOT NULL")
                            matches = cursor.fetchone()[0]

                    else:
                        # Non-select queries (e.g., INSERT, UPDATE) can be handled here
                        connection.commit()

            except Exception as e:
                error = str(e)
    else:
        form = SQLQueryForm()

    return render(request, 'validation_app/sql_query_form.html', {
        'form': form,
        'columns': columns,
        'results': results,
        'total_count': total_count,
        'total_nulls': total_nulls,
        'mismatches': mismatches,
        'matches': matches,
        'error': error
    })




def validation_type_for_multi(request):
    results = None
    error = None
    columns = []
    analytics = defaultdict(dict)  # Store total count, nulls, etc.

    if request.method == 'POST':
        form = SQLQueryForm(request.POST)
        sql_query = request.POST.get('sql_query', '').strip()

        if sql_query:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(sql_query)

                    # Get column names
                    columns = [col[0] for col in cursor.description]

                    # Fetch all rows
                    results = cursor.fetchall()

                    # Total row count
                    total_rows = len(results)

                    # Analyze null counts for each column
                    for col_idx, col_name in enumerate(columns):
                        null_count = sum(1 for row in results if row[col_idx] is None)
                        analytics[col_name]['null_count'] = null_count

                    # Add total rows to analytics
                    analytics['total_rows'] = total_rows

            except Exception as e:
                error = str(e)
    else:
        form = SQLQueryForm()

    return render(request, 'validation_app/sql_query_form.html', {
        'form': form,
        'columns': columns,        # Column names
        'results': results,        # Query results
        'analytics': analytics,    # Analysis data
        'error': error,            # Errors (if any)
    })


def validation_type(request):
    results = None
    error = None
    columns = []
    analytics = defaultdict(dict)  # Store total count, nulls, etc.

    if request.method == 'POST':
        form = SQLQueryForm(request.POST)
        sql_query = request.POST.get('sql_query', '').strip()

        if sql_query:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(sql_query)

                    # Get column names
                    columns = [col[0] for col in cursor.description]

                    # Fetch all rows
                    results = cursor.fetchall()

                    
                    # Extract table names from the query (basic parsing for demo purposes)
                    tables = [word for word in sql_query.split() if word.lower() not in ('select', 'from', 'join', 'on', 'where', 'and', 'or')]

                    # Analyze total record counts in each table
                    for table in tables:
                        if table.isidentifier():  # Skip keywords or invalid table names
                            cursor.execute(f"SELECT COUNT(*) FROM {table}")
                            total_count = cursor.fetchone()[0]
                            analytics[table]['total_count'] = total_count

                    # Optional: Handle unmatched records (modify query for unmatched rows)
                    if 'join' in sql_query.lower():
                        # Emulate FULL OUTER JOIN for MariaDB/MySQL
                        left_query = sql_query.replace('JOIN', 'LEFT JOIN')
                        right_query = sql_query.replace('JOIN', 'RIGHT JOIN')
                        full_outer_query = f"{left_query} UNION {right_query}"
                        print("Executing Full Outer Query:", full_outer_query)  # Debugging
                        cursor.execute(full_outer_query)
                        unmatched_results = cursor.fetchall()
                        analytics['unmatched_records'] = len(unmatched_results)

                    # Total rows in the original result
                    analytics['total_rows'] = len(results)

            except Exception as e:
                error = str(e)
    else:
        form = SQLQueryForm()

    return render(request, 'validation_app/sql_query_form.html', {
        'form': form,
        'columns': columns,        # Column names
        'results': results,        # Query results
        'analytics': analytics,    # Analysis data
        'error': error,            # Errors (if any)
    })

def mapping(request):
    results = None
    error = None

    if request.method == 'POST':
        form = SQLQueryForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['sql_query']
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    if query.lower().strip().startswith("select"):
                        results = cursor.fetchall()
                    else:
                        connection.commit()
            except Exception as e:
                error = str(e)
    else:
        form = SQLQueryForm()

    return render(request, 'validation_app/sql_query_form.html', {
        'form': form,
        'results': results,
        'error': error
    })

def result(request):
    results = None
    error = None

    if request.method == 'POST':
        form = SQLQueryForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['sql_query']
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    if query.lower().strip().startswith("select"):
                        results = cursor.fetchall()
                    else:
                        connection.commit()
            except Exception as e:
                error = str(e)
    else:
        form = SQLQueryForm()

    return render(request, 'validation_app/sql_query_form.html', {
        'form': form,
        'results': results,
        'error': error
    })