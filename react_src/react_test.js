// import data from 'json!./data.json';
// import data from './data.json';

function Item(props) {
    return <li>{props.message}</li>;
}

export function TodoList(props) {
    const todos = ['finish doc', 'submit pr', 'nag dan to review'];
    var origin = props["add"]?props["add"]:"";
    todos.push(origin);
    return (
        <ul>
            {todos.map((message) => <Item key={message} message={message} />)}
        </ul>
    );
}

// equal
// {todos.map(function(message){return (<Item key={message} message={message} />);})}
// {todos.map((message) => <Item key={message} message={message} />)}

function Repeat(props) {
    console.log();
    if( !Array.isArray(props.children) ){
        var child = [props.children];
    }else{
        var child = props.children
    }
    
    // propsにはchildrenとnumTimesが入る
    console.log(props.children.toString());
    // console.log(data.stringify(props.children[2]));
    console.log(props.children.length);
    let items = [];
    for (let i = 0; i < props.numTimes; i++) {
        let i2 = i%props.children.length;
        if (typeof (props.children[i2]) === 'function'){
            items.push(props.children[i2](i,i-1));
        }else{
            items.push(props.children[i2]);
        }
    }
    return <div>"1"{items}</div>;
}

export function ListOfTenThings() {
    return (
        <Repeat numTimes={10}>
            {function(index,index2){ return (<div key={index}>This is item {index}{index2} in the list</div>); }}
            {function(index,index2){ return (<div key={index}>This is item {index2}{index} in the list</div>); }}
            {<TodoList add="test1"/>}
            <TodoList add="test2"/>
        </Repeat>
    );
}


export function OutputList(){
    const listed = [];
    listed.push(<p>a</p>)
    listed.push(<p>a</p>)
    return (<>{listed}</>);
}
// <>
// ここの内容はchildrenという値で入力される
// 複数行存在する場合は自動的に配列になる
// 
// <～/>
            // {(index) => <div key={index}>This is item {index} in the list</div>}

//// 最上位のエレメントが複数ある場合、エラー
// export function TestView(props){
//     return (
//         <Testpart1 type={1} /> 
//         <Testpart2 type={1} />
//     );
// }

