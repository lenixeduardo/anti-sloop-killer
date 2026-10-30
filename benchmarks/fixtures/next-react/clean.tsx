import Image from 'next/image';
export default function Home() {
  return <main>
    <Image src="/hero.jpg" width={400} height={300} alt="Portfólio"/>
    <a href="#contato">Contato</a>
    <section id="contato"><h2>Contato</h2></section>
    <button onClick={() => alert('enviado')}>Enviar</button>
    <label htmlFor="telefone">Telefone</label><input id="telefone" type="tel" />
    <button type="button" aria-label="Mostrar detalhes"><svg aria-hidden="true" /></button>
    <form><button type="submit">Enviar formulário</button></form>
    <a href="/externo" target="_blank" rel="noopener noreferrer">Outro site</a>
    <iframe title="Vídeo de apresentação" src="/videos/intro" />
    {/* Exemplo em comentário: <img src="bad"> */}
  </main>;
}
