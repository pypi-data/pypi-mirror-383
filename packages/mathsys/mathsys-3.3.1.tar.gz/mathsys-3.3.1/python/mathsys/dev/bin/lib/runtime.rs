//
//  CONTEXT
//

// CONTEXT -> VALUE
pub trait Value {
    fn id(&self) -> &'static str;
}

// CONTEXT -> ID
pub trait Id {
    const ID: &'static str;
}

// CONTEXT -> STRUCT
pub struct Context<'a> {
    cache: crate::Vec<crate::Box<dyn Value>>,
    memory: &'a crate::Vec<crate::Box <dyn crate::converter::Class>>,
    pub mutable: crate::Vec<(crate::String, crate::Box<dyn Value>)>,
    pub immutable: crate::Vec<(crate::String, crate::Box<dyn Value>)>
}

// CONTEXT -> IMPLEMENTATION
impl<'a> Context<'a> {
    pub fn new(size: usize, memory: &'a crate::Vec<crate::Box <dyn crate::converter::Class>>) -> Self {
        let mut instance = Context {
            cache: crate::Vec::with_capacity(size),
            memory: memory,
            mutable: crate::Vec::new(),
            immutable: crate::Vec::new()
        };
        for index in 0..size {instance.cache.push(crate::Box::new(crate::_Undefined {}))};
        return instance;
    }
    fn set(&mut self, id: u32, value: crate::Box<dyn Value>) {self.cache[(id as usize) - 1] = value}
    fn get(&self, id: u32) -> &dyn Value {return &*self.cache[(id as usize) - 1]}
    pub fn process(&mut self, id: u32) -> &dyn Value {
        let output = self.memory[(id as usize) - 1].evaluate(self);
        self.set(id, output);
        return self.get(id);
    }
    pub fn quick(&mut self) -> &dyn Value {
        for (index, element) in self.memory.iter().enumerate() {
            if element.as_ref().name() == "Start" {
                return self.process((index + 1) as u32);
            }
        }
        crate::stdout::crash(3);
    }
}


//
//  DOWNCASTING
//

// DOWNCASTING -> STATIC
pub fn downcast<Type: Id>(value: &dyn Value) -> &Type {
    if value.id() != Type::ID {crate::stdout::crash(3)} else {
        return unsafe {&*(value as *const dyn Value as *const Type)}
    }
}

// DOWNCASTING -> MUTABLE
pub fn mutDowncast<Type: Id>(value: &mut dyn Value) -> &mut Type {
    if value.id() != Type::ID {crate::stdout::crash(3)} else {
        return unsafe {&mut *(value as *mut dyn Value as *mut Type)}
    }
}