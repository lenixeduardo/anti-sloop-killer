import Image from 'next/image';
export default function Home() {
  return <main>
    <Image src="/hero.jpg" width={400} height={300}/>
    <a href={"#"}>Conhecer</a>
    <div onClick={() => { alert('ok'); }}>Abrir</div>
    <button onClick={() => { /* ação ainda não implementada */ }}>Enviar</button>
    <iframe src="/videos/intro" />
    <img src="" alt="" />
    <button aria-hidden="true">Oculto</button>
    <input id="telefone" type="text" />
    <a href="/externo" target="_blank">Outro site</a>
    <form><button>Cancelar</button></form>
    <button aria-label="Ação sem imagem" />
  </main>;
}
