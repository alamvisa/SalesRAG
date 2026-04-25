# SalesRAG

```



Tests:

There are integration tests written to tests directory which test that the basic input-outputs of the RAG are correctly formatted and structured. The tests also query the RAG model with sample queries to check wether correct context is retrieved. These queries do take some time and if running the models on CPU the entire test suite will take significant time.

To test the RAG 
Run "pytest test_pipeline.py -v"
"""