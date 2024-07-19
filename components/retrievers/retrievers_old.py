import os,logging
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import pandas as pd

def rerank_norm_dist(documents,top_n):
    document_metadata = [{"document_id": doc[0].metadata["label_03"], "distance": doc[1]} for i, doc in enumerate(documents)]
    df_metadata = pd.DataFrame(document_metadata)
    max_dist = df_metadata["distance"].max()
    min_dist = df_metadata["distance"].min()
    norm_denom = max_dist - min_dist
    df_metadata['distance_normalized'] = (df_metadata['distance'] - min_dist) / norm_denom
    # Group by document_id and sum up the distance_normalized values
    top_docs = df_metadata.groupby('document_id')['distance_normalized'].agg(['mean', 'count'])

    # Get the top 5 documents with the lowest sum of distance_normalized
    top_documents = top_docs.nsmallest(top_n,columns='mean')
    docs = top_documents.to_dict(orient='index')
    doc_list = top_documents.index.tolist()
    
    results = {"top_documents": doc_list, "document_metadata": docs}
    return results

def document_retriever_tool(court_id,data_exchanges,query,search_top_k,user_filter,retrieved_documents,retrieved_top_k):
    """
    query = "What is the filing type for an answer to complaint?"
    query = "list the required documents and forms to initiate a complaint"
    court_id = '1'
    data_exchanges = [123,132]
    top_k = 12
    user_filter = {}
    search_top_k = 10
    retrieved_documents = 5
    retrieved_top_k = 10


    """
    embedder = embedder_open_ai()
    tmp_storage = udf_file_paths.udf_get_local_storage()
    system_filter = {"label_01": int(court_id),"label_02":data_exchanges}

    complete_filter = {**system_filter,**user_filter}
    
    i = 0
    for data_exchange_id in data_exchanges:
        try:
            index_path = os.path.join(tmp_storage, 'indexes/final',str(court_id),'data_exchanges',str(data_exchange_id))
            index_temp = FAISS.load_local(index_path, embedder,allow_dangerous_deserialization=True)
            if i == 0:
                index_main = index_temp
            else:
                index_main.merge_from(index_temp)
        except Exception as e:
            logging.error(e)
        i = i +1

    similar_docs_00 = index_main.similarity_search_with_score(query,k = search_top_k,filter = complete_filter,fetch_k=10000)

    top_matches = rerank_norm_dist(similar_docs_00,retrieved_documents)
    doc_filter = {"label_03": top_matches['top_documents']}
    final_filter = {**complete_filter,**doc_filter}

    similar_docs = index_main.similarity_search_with_score(query,k = retrieved_top_k,filter = final_filter,fetch_k=10000)
    
    raw_text = '\n'.join([item[0].page_content for item in similar_docs])

    chat_response_citations = {} 

    for item in similar_docs:

        document_id = item[0].metadata['label_03']  
        if document_id not in chat_response_citations:  
            chat_response_citations[document_id] = {
                "original_document_name": item[0].metadata['label_04'],
                "document_tag": item[0].metadata['label_04'] ,
                "texts": []  
            }  
        chat_response_citations[document_id]["texts"].append({  
            "@search.score": float(item[1]), 
            "page": int(item[0].metadata['page']),
            "text": item[0].page_content
        }) 


    return {"chat_response_citations":chat_response_citations,"raw_text":raw_text}


