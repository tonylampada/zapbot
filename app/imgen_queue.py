import threading
import queue
import zap
import imgen

GLOBAL = {}
# Create a global queue
image_queue = queue.Queue()

def add_imgen_job(user, prompt):
    _start()
    queue_size = image_queue.qsize()
    zap.send_message('jarbas', user, f"Enfileirando imagem... ({queue_size} na fila)")
    image_queue.put((user, prompt))

def process_image_queue():
    while True:
        user, prompt = image_queue.get()
        try:
            zap.send_message('jarbas', user, "Gerando imagem...")
            img_base64 = imgen.generate(prompt)
            zap.send_image('jarbas', user, "imagem.png", "", img_base64)
        except Exception as e:
            zap.send_message('jarbas', user, f"Erro ao gerar imagem: {e}")
        finally:
            image_queue.task_done()

def _start():
    if not GLOBAL.get('started'):
        GLOBAL['started'] = True
        threading.Thread(target=process_image_queue, daemon=True).start()
