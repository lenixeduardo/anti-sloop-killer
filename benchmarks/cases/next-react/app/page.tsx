import Image from 'next/image';
export default function Page(){
const example = `<img src="fake.jpg" /><a href="#">FAKE</a>`;
return <main><Image src="/hero.webp" width={720} height={400} />
<Link href={"#"}>Comprar</Link><div onClick={() => save()}>Salvar</div>
<button onClick={() => {/* TODO */}}>Enviar</button><input placeholder="Buscar" /></main>;
}
function Link(props:any){return <a href={props.href}>{props.children}</a>};
function save(){}
