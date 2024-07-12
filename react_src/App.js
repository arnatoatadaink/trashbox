import React from 'react';
import './App.css';
import './loader.css';

import {
    PageController,
    LoginView,
} from './view_parts';

class App extends React.Component{
    constructor(props){
        super(props);
        console.log("app constructor");
    }
    render(){
        return (<>
            <LoginView view={PageController}/>
        </>);
    }
}

export default App;

