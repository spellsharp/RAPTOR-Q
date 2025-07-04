from dotenv import load_dotenv
from langchain.schema.runnable import RunnableSequence
from utils.lm_studio import LMStudioLLM
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain.schema.runnable import RunnableLambda
from src.translation import translation_template
from src.routing import semantic_routing_template
from src.indexing import indexing_template, extract_questions
from src.raptor import raptor_template
from src.retrieval import retrieval_template
from src.generation import generation_template
from utils.pdf_summarizer import get_summaries

# Load environment variables
load_dotenv()

# Initialize LLM, number of splits to retrieve, text splitter, and the embedder
lm_studio_llm = LMStudioLLM(path='completions')
top_k_indexing = 50
top_k_retrieval = 7
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size = 300,
    chunk_overlap = 50
)
embedder = GPT4AllEmbeddings()

# Input question
question = {'question': input("Please enter your question: ")}

# Gather files
files = []
for i in range(int(input("Enter the number of files: "))):
    files.append(input("Enter file name: "))

# Precompute translation_output
translation_result = translation_template() | lm_studio_llm
translation_output = translation_result.invoke(question)

question_list = extract_questions(translation_output)
print("The questions are: ")
for i in question_list:
    print(i)

print("\nGenerating summaries for the files mentioned...")
# Generate file summaries
file_summaries = ""
if len(files) > 0:
    # summaries in the format [[file_name, summary], ..]
    summaries = get_summaries(files)
    file_summaries = "\n".join([f"{file}: {summary}" for file, summary in summaries])

print("Generated summaries for the files.\n")
# Define llm_chain for file input
llm_chain_file = RunnableSequence(
    # Logical routing
    # RunnableLambda(lambda question: logical_routing_template().format(
    #     question=question['question'],  
    #     file_summaries=file_summaries  
    # )) | 
    # lm_studio_llm |

    # Semantic routing
    RunnableLambda(lambda _: semantic_routing_template()(
        questions=translation_output,
        file_summaries=summaries,
        embedder=embedder
    )) |

    # Indexing
    RunnableLambda(lambda doc_name_list: indexing_template()(
        documents=doc_name_list,
        questions=translation_output,
        text_splitter=text_splitter,
        embedder=embedder,
        top_k=top_k_indexing
    )) |

    # Raptor retrieval
    RunnableLambda(lambda splits_list: raptor_template()(
        doc_splits=splits_list,
        questions=translation_output,
        embedder=embedder
    )) |
    RunnableLambda(lambda best_cluster_nodes: retrieval_template()(
        best_cluster_nodes=best_cluster_nodes,
        questions=translation_output,
        embedder=embedder,
        top_k=top_k_retrieval
    )) |
    (lambda best_nodes: generation_template().format(
        question=question['question'],
        best_nodes=best_nodes
    )) |
    lm_studio_llm
)

# Define llm_chain for no file input
llm_chain_no_file = RunnableSequence(
    translation_template() | lm_studio_llm
)

# Execute chain based on files
if len(files) == 0:
    answer = llm_chain_no_file.invoke(question)
else:
    answer = llm_chain_file.invoke({
        'question': question,
        'file_summaries': file_summaries
    })

print("The answer to your question after completing RAG is:\n", answer)